from odoo import models, fields, api, _

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.

class IdeaManagement(models.Model):
   _name = 'idea.management'
   _description = 'Idea'

   name = fields.Char(string = 'Nombre de la idea', default="Idea")
   create_date = fields.Date(string = 'Fecha de creación', default=_date_default_today)
   deadline = fields.Date(string = 'Fecha límite')
   idea_type = fields.Selection(
      [('mejoras', 'Mejoras'),
      ('proyecto', 'Plantear proyecto'),], 
      string="Tipo de idea")
   details = fields.Text()
   price = fields.Float(string="Coste estimado")
   state = fields.Selection(
      [('revision', 'En revision'), 
      ('aprobada','Aprobada'),
      ('proceso', 'En proceso'),
      ('completada', 'Completada'),
      ('cancelada', 'Cancelada')],
      string = 'Estado',
      default = 'revision')
   
   company_id = fields.Many2one(comodel_name='res.partner', string='Compañía')
   user_id = fields.Many2one(comodel_name='res.users', string='Empleados')
   # partner_id = fields.Many2one(comodel_name='hr.employee', string='Empleado')
   # department_id = fields.Many2one(comodel_name='hr.department', string='Departamento')
   
   def aprobar(self):
      self.ensure_one()
      self.write({
         'state': 'aprobada'})
      
   def proceso(self):
      self.ensure_one()
      self.state = 'proceso'

   def completada(self):
      self.ensure_one()
      self.state = 'completada'

   def cancelada(self):
      self.ensure_one()
      self.state = 'cancelada'       