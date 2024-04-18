from odoo import models, api, fields, _

class Vote(models.Model):
    _name = 'idea.vote'
    _description = 'Vote'

    rating = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High'), ('4', 'Very High'), ('5', 'Excellent')], string="Valoraciones")
    comments = fields.Text(string = "Comentarios")
    idea_id = fields.Many2one('idea.management', string='Idea')
    voter_id = fields.Many2one('res.users', string='Voter')
    # Otros campos para almacenar información sobre el voto

    