##############################################################################
#
#    Copyright (C) 2019 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from odoo import api, fields, models


class DemandPlanningSettings(models.TransientModel):
    _inherit = "res.config.settings"

    s2b_template_default_id = fields.Many2one(
        "correspondence.template", "Default S2B template", readonly=False
    )

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].set_param(
            "mobile_app_connector.s2b_template",
            str(self.s2b_template_default_id.id or 0),
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        param_obj = self.env["ir.config_parameter"].sudo()
        s2b_template_id = int(
            param_obj.get_param("mobile_app_connector.s2b_template", "0")
        )
        res.update(
            {
                "s2b_template_default_id": s2b_template_id,
            }
        )
        return res
