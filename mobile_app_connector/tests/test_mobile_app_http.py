##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Nicolas Bornand
#
#    The licence is in the file __manifest__.py
#
##############################################################################
import simplejson
from mock import patch

from odoo.tests.common import HttpCase

mock_oauth = (
    "odoo.addons.message_center_compassion.models.ir_http" ".IrHTTP._oauth_validation"
)


class TestMobileAppHttp(HttpCase):
    admin_username = "admin"
    admin_password = "admin"

    def setUp(self):
        super().setUp()
        self.root_url = "/mobile-app-api/"
        # Add JSON type in request headers and fake token
        self.opener.headers.update({"Content-Type": "application/json"})
        self.opener.headers.update({"Authorization": "Bearer fake_token"})

    @patch(mock_oauth)
    def test_login(self, oauth_patch):
        oauth_patch.return_value = "admin"
        url = self.root_url + "login?username={}&password={}"
        # Bad username and password
        response = self.url_open(url.format("wrong", "login"))
        self.assertEqual(response.status_code, 200)
        json_data = simplejson.loads(response.content)
        self.assertEqual(json_data["error"], "Wrong user or password")
        # Good username and password
        response = self.url_open(url.format(self.admin_username, self.admin_password))
        self.assertEqual(response.status_code, 200)
        json_data = simplejson.loads(response.content)
        self.assertEqual(json_data["userid"], str(self.env.ref("base.user_admin").id))

    @patch(mock_oauth)
    def test_hub_authentication(self, oauth_patch):
        """
        Tests for the hub messages security:
        - if no partner is specified, the url is publicly available
        - if a partner is requested, the user must be authenticated
        """
        oauth_patch.return_value = "admin"
        url = self.root_url + "hub/"
        # Public messages
        response = self.url_open(url + "0")
        self.assertEqual(response.status_code, 200)
        json_data = simplejson.loads(response.content)
        self.assertIn("Messages", json_data)
        # Private messages without login should fail
        response = self.url_open(url + str(self.env.ref("base.partner_admin").id))
        self.assertEqual(response.status_code, 401)
        # Private message while authenticated should work
        self.authenticate(self.admin_username, self.admin_password)
        response = self.url_open(url + str(self.env.ref("base.partner_admin").id))
        self.assertEqual(response.status_code, 200)
        json_data = simplejson.loads(response.content)
        self.assertIn("Messages", json_data)

    def test_entry_point(self):
        # Test we can only call entry point while authenticated
        self.env["res.users"].sudo().browse(1).partner_id.ref = "1818"
        url = self.root_url + "compassion.child/sponsor_children?userid=1818"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 401)
        self.authenticate(self.admin_username, self.admin_password)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)

    def test_get_message_hub(self):
        # Test we can only call hub entry point for user while authenticated
        url = self.root_url + "hub/0"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        url = self.root_url + "hub/" + str(self.env.ref("base.partner_admin").id)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 401)
        self.authenticate(self.admin_username, self.admin_password)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
