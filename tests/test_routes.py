"""
Account API Service Test Suite
Run with:
    nosetests -v --with-spec --spec-color
    coverage report -m
"""
import os
import logging
from unittest import TestCase
from service.common import status
from service.models import db, Account, init_db
from service.routes import app
from tests.factories import AccountFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/accounts"

class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.session.query(Account).delete()
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()

    # Helper method to create accounts
    def _create_accounts(self, count=1):
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            resp = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            new_account = resp.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    # -------------------- TEST CASES --------------------
    def test_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["status"], "OK")

    def test_create_account(self):
        account = AccountFactory()
        resp = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(resp.headers.get("Location"))
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name)

    def test_bad_request(self):
        resp = self.client.post(BASE_URL, json={"name": "short"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        account = AccountFactory()
        resp = self.client.post(BASE_URL, json=account.serialize(), content_type="text/plain")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_account(self):
        account = self._create_accounts()[0]
        resp = self.client.get(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["name"], account.name)

    def test_get_account_not_found(self):
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_account_list(self):
        self._create_accounts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 5)

    def test_update_account(self):
        account = self._create_accounts()[0]
        account_data = account.serialize()
        account_data["name"] = "Updated Name"
        resp = self.client.put(f"{BASE_URL}/{account.id}", json=account_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["name"], "Updated Name")

    def test_update_account_not_found(self):
        account_data = AccountFactory().serialize()
        resp = self.client.put(f"{BASE_URL}/0", json=account_data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account(self):
        account = self._create_accounts()[0]
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_account_not_found(self):
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        resp = self.client.delete(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
