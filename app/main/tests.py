import sys
from io import StringIO

from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command

from .models import Drone, Medication
from .exceptions import DroneBaterryTooLowError, DroneInvalidStateError

class DroneTestCase(TestCase):
    """
    Test some features of model Drone & his respective endpoint
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client(
            HTTP_CONTENT_TYPE='text/json'
        )

        self.drone_1 = Drone.objects.get(serial_number='DRONE_1')
        self.dron_low_baterry = Drone.objects.get(serial_number='DRON_LOW_BATERRY')

        self.med_item = Medication.objects.get(code='ASP_755')
        self.med_item_to_heavy = Medication.objects.get(code='TO_HEAVY_ITEM')
    
    def test_set_state_from_idle(self):
        """
        Test set new state from "IDLE"
        """
        self.assertEqual(self.drone_1.state, Drone.STATE_IDLE)

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_LOADED)
            self.drone_1.set_state(Drone.STATE_DELIVERING)
            self.drone_1.set_state(Drone.STATE_DELIVERED)
            self.drone_1.set_state(Drone.STATE_RETURNING)

        self.drone_1.set_state(Drone.STATE_LOADING)
        self.assertEqual(self.drone_1.state, Drone.STATE_LOADING)
 
    def test_set_state_from_loading(self):
        """
        Test set new state from "LOADING"
        """
        self.drone_1.state = Drone.STATE_LOADING
        self.drone_1.save()

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_DELIVERING)
            self.drone_1.set_state(Drone.STATE_DELIVERED)
            self.drone_1.set_state(Drone.STATE_RETURNING)
        
        self.drone_1.set_state(Drone.STATE_LOADED)
        self.assertEqual(self.drone_1.state, Drone.STATE_LOADED)

    def test_set_state_from_loaded(self):
        """
        Test set new state from "LOADED"
        """
        self.drone_1.state = Drone.STATE_LOADED
        self.drone_1.save()

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_DELIVERED)
            self.drone_1.set_state(Drone.STATE_RETURNING)
        
        self.drone_1.set_state(Drone.STATE_DELIVERING)
        self.assertEqual(self.drone_1.state, Drone.STATE_DELIVERING)

    def test_set_state_from_delivering(self):
        """
        Test set new state from "DELIVERING"
        """
        self.drone_1.state = Drone.STATE_DELIVERING
        self.drone_1.save()

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_IDLE)
            self.drone_1.set_state(Drone.STATE_LOADING)
            self.drone_1.set_state(Drone.STATE_LOADED)
        
        self.drone_1.set_state(Drone.STATE_DELIVERED)
        self.assertEqual(self.drone_1.state, Drone.STATE_DELIVERED)
    
    def test_set_state_from_delivered(self):
        """
        Test set new state from "DELIVERED"
        """
        self.drone_1.state = Drone.STATE_DELIVERED
        self.drone_1.save()

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_IDLE)
            self.drone_1.set_state(Drone.STATE_LOADING)
            self.drone_1.set_state(Drone.STATE_LOADED)
            self.drone_1.set_state(Drone.STATE_DELIVERING)
        
        self.drone_1.set_state(Drone.STATE_RETURNING)
        self.assertEqual(self.drone_1.state, Drone.STATE_RETURNING)
    
    def test_set_state_from_returning(self):
        """
        Test set new state from "RETURNING"
        """
        self.drone_1.state = Drone.STATE_RETURNING
        self.drone_1.save()

        with self.assertRaises(DroneInvalidStateError):
            self.drone_1.set_state(Drone.STATE_LOADING)
            self.drone_1.set_state(Drone.STATE_LOADED)
            self.drone_1.set_state(Drone.STATE_DELIVERING)
            self.drone_1.set_state(Drone.STATE_DELIVERED)
        
        self.drone_1.set_state(Drone.STATE_IDLE)
        self.assertEqual(self.drone_1.state, Drone.STATE_IDLE)

    def test_set_state_drone_baterry_too_low(self):
        """
        Test set new state for a drone with low baterry
        """
        with self.assertRaises(DroneBaterryTooLowError):
            self.dron_low_baterry.set_state(Drone.STATE_LOADING)

    def test_drone_list_view(self):
        """
        Test drone listing endpoint
        """
        response = self.client.get(reverse('drone-list'))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json()), 2)

        ids, serial_number = zip(*map(lambda d: (d['id'], d['serial_number']), response.json()))

        self.assertIn(self.drone_1.id, ids)
        self.assertIn(self.dron_low_baterry.id, ids)

        self.assertIn(self.drone_1.serial_number, serial_number)
        self.assertIn(self.dron_low_baterry.serial_number, serial_number)

    def test_get_available_drones_for_load(self):
        """
        Test drone listing endpoint
        """
        response = self.client.get(reverse('drone-get-available-drones-for-load'))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json()), 1)

        ids, serial_number = zip(*map(lambda d: (d['id'], d['serial_number']), response.json()))

        self.assertIn(self.drone_1.id, ids)
        self.assertIn(self.drone_1.serial_number, serial_number)

    def test_get_drone_baterry(self):
        """
        Test drone baterry endpoint
        """
        response = self.client.get(
            reverse('drone-get-baterry', kwargs={'pk': self.drone_1.pk})
        )

        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(response.content, {"battery_capacity": 100.0})
    
    def test_drone_set_state_endpoint(self):
        """
        Test drone set state endpoint
        """
        data = {'state': Drone.STATE_LOADING}

        response = self.client.post(
            reverse('drone-set-state', kwargs={'pk': self.drone_1.pk}),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, data)
    
    def test_drone_load_medication_item(self):
        """
        Test drone load medication item endpoint
        """
        self.drone_1.set_state(Drone.STATE_LOADING)

        response = self.client.post(
            reverse('drone-load-medication-item', kwargs={'pk': self.drone_1.pk}),
            {'medication_item_id': self.med_item.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'detail': 'The item has been loaded successfully.'})

    def test_drone_load_medication_item_too_heavy(self):
        """
        Test drone load medication item endpoint with too heavy med item
        """
        self.drone_1.set_state(Drone.STATE_LOADING)

        response = self.client.post(
            reverse('drone-load-medication-item', kwargs={'pk': self.drone_1.pk}),
            {'medication_item_id': self.med_item_to_heavy.pk}
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"detail":"Drone weight limit exceeded, can\'t load the item."})

    def test_drone_get_loaded_medication_items(self):
        """
        Test drone to get loaded med items
        """
        self.drone_1.set_state(Drone.STATE_LOADING)

        response = self.client.post(
            reverse('drone-load-medication-item', kwargs={'pk': self.drone_1.pk}),
            {'medication_item_id': self.med_item.pk}
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('drone-get-loaded-medication-items', kwargs={'pk': self.drone_1.pk}))

        self.assertEqual(len(response.json()), 1)

        self.assertEqual(response.json()[0]['id'], self.med_item.pk)
        self.assertEqual(response.json()[0]['name'], self.med_item.name)
        self.assertEqual(response.json()[0]['code'], self.med_item.code)

    def test_check_drones_baterry_command(self):
        """
        Test check_drones_baterry command
        """
        stdout = sys.stdout

        sys.stdout = StringIO()

        call_command('check_drones_baterry')
        
        output = sys.stdout.getvalue()
        
        sys.stdout = stdout

        self.assertIn('Drone DRONE_1 has enough battery to fly', output)
        self.assertIn('Drone DRON_LOW_BATERRY has low battery', output)
