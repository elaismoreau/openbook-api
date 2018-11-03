# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from mixer.backend.django import mixer

from openbook_auth.models import User
from faker import Faker

import logging
import json

from openbook_circles.models import Circle
from openbook_common.models import Emoji
from openbook_connections.models import Connection

logger = logging.getLogger(__name__)

fake = Faker()


class ConnectionsAPITests(APITestCase):
    """
    ConnectionsAPI
    """

    def test_retrieve_own_connections(self):
        """
        should be able to retrieve own connections and return 200
        """
        user = mixer.blend(User)
        auth_token = user.auth_token.key
        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        circle = mixer.blend(Circle, creator=user)

        users_to_connect = mixer.cycle(5).blend(User)
        user_to_connect_ids = [user_to_connect.pk for user_to_connect in users_to_connect]

        for user_to_connect in users_to_connect:
            user.connect_with_user(user_to_connect, circle=circle)

        url = self._get_url()
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_connections = json.loads(response.content)

        self.assertEqual(len(response_connections), len(users_to_connect))

        for response_connection in response_connections:
            target_user = response_connection.get('target_user')
            target_user_id = target_user.get('id')
            self.assertIn(target_user_id, user_to_connect_ids)

    def _get_url(self):
        return reverse('connections')


class ConnectAPITests(APITestCase):
    def test_connect(self):
        """
        should be able to connect with another user on an specific circle and return 200
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        circle_to_connect = mixer.blend(Circle, creator=user)
        user_to_connect = mixer.blend(User)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': user_to_connect.pk,
            'circle_id': circle_to_connect.pk
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(user.is_connected_with_user_in_circle(user_to_connect, circle_to_connect))

    def test_cannot_connect_with_existing_connection(self):
        """
        should not be able to connect with a user already connected with and return 400
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        circle_to_connect = mixer.blend(Circle, creator=user)
        user_to_connect = mixer.blend(User)

        user.connect_with_user(user_to_connect, circle=circle_to_connect)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': user_to_connect.pk,
            'circle_id': circle_to_connect.pk
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_connect_in_world_circle(self):
        """
        should not be able to connect with a user in the world circle and return 400
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        user_to_connect = mixer.blend(User)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': user_to_connect.pk,
            'circle_id': user.world_circle_id
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_url(self):
        return reverse('connect-with-user')


class DisconnectAPITest(APITestCase):
    def test_disconnect(self):
        """
        should be able to disconnect from a user and return 200
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        circle_to_connect = mixer.blend(Circle, creator=user)
        user_to_connect = mixer.blend(User)

        user.connect_with_user(user_to_connect, circle=circle_to_connect)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': user_to_connect.pk
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(user.is_connected_with_user_in_circle(user_to_connect, circle_to_connect))

    def test_cannot_disconnect_from_unexisting_connection(self):
        """
        should not be able to disconnect from an unexisting connection and return 400
        """
        user = mixer.blend(User)

        not_connected_user = mixer.blend(User)

        auth_token = user.auth_token.key

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': not_connected_user
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(user.is_connected_with_user(not_connected_user))

    def _get_url(self):
        return reverse('disconnect-from-user')


class UpdateConnectionAPITest(APITestCase):
    def test_update_connection(self):
        """
        should be able to update an own connection and return 200
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        circle_to_connect = mixer.blend(Circle, creator=user)
        user_to_connect = mixer.blend(User)

        user.connect_with_user(user_to_connect, circle=circle_to_connect)

        new_circle = mixer.blend(Circle, creator=user)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': user_to_connect.pk,
            'circle_id': new_circle.pk
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(user.is_connected_with_user_in_circle(user_to_connect, new_circle))
        self.assertFalse(user.is_connected_with_user_in_circle(user_to_connect, circle_to_connect))

    def test_cannot_update_unexisting_connection(self):
        """
        should not be able to update an unexisting connection and return 400
        """
        user = mixer.blend(User)

        auth_token = user.auth_token.key

        not_connected_user = mixer.blend(User)

        new_circle = mixer.blend(Circle, creator=user)

        headers = {'HTTP_AUTHORIZATION': 'Token %s' % auth_token}

        data = {
            'user_id': not_connected_user.pk,
            'circle_id': new_circle.pk
        }

        url = self._get_url()

        response = self.client.post(url, data, **headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_url(self):
        return reverse('update-connection')
