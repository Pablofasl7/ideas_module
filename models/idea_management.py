from odoo import models, fields, api, _

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.

class IdeaManagement(models.Model):
   _name = 'idea.management'
   _description = 'Idea'

   name = fields.Char(string = 'Nombre de la idea')
   create_date = fields.Date(string = 'Fecha de creación', default=_date_default_today)
   deadline = fields.Date(string = 'Fecha límite')
   idea_type = fields.Selection(
      [('mejoras', 'Mejoras'),
      ('proyecto', 'Plantear proyecto'),], 
      string="Tipo de idea")
   details = fields.Text()
   
   company_id = fields.Many2one(comodel_name='res.partner', string='Compañía')
   user_id = fields.Many2one(comodel_name='res.users', string='Empleados')
   