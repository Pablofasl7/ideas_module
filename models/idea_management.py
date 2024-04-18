from odoo import models, fields, api, _

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.

class IdeaManagement(models.Model):
   _name = 'idea.management'
   _description = 'Idea'

   name = fields.Char(string = 'Nombre de la idea', required=True)
   create_date = fields.Date(string = 'Fecha de creación', default=_date_default_today)
   deadline = fields.Date(string = 'Fecha límite')

   employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado')