from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import base64

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.

class IdeaManagementVote(models.Model):
   _name = 'idea.management.vote'
   _description = 'Idea Management Vote'

   rating = fields.Selection(
      [('0', 'Very Low'), ('1', 'Baja'), ('2', 'Normal'), ('3', 'Alto'), ('4', 'Muy alto'), ('5', 'Excelente')],
      string="Valoraciones")
   comments = fields.Char(string="Comentarios", help="Aquí puedes dejar comentarios que leerán tanto los administradores como los demás usuarios (por ejemplo para mejorar la idea).")
   employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado', help="El empleado que ha votado la idea.")
   idea_id = fields.Many2one('idea.management', string='Nombre de la idea', readonly=True, help="La idea que ha votado.")
   
   def save_vote(self):
      print(self.employee_id.name)
      for idea in self.env['idea.management'].search([]):
         for employee in idea.employee_id:
            if employee.id != self.employee_id.id:
               new_vote = self.env['idea.management.vote'].write({
                     'employee_id': self.employee_id.id,
                        'rating': self.rating,
                        'comments': self.comments,
               })
            else:
               raise ValidationError(_("No puedes votar dos veces a la misma idea."))

   # Obtenemos el voto del empleado actual y si le damos al botón cancelar, no guardamos el boto (lo eliminamos)
   def cancel_vote(self):
      id_vote = self.env.context.get('active_id')  
      if id_vote:
         idea_record = self.env['idea.management'].browse(id_vote) 
         if idea_record:
            last_vote = idea_record.vote_ids[-1] 
            last_vote.unlink()  
   
class IdeaManagement(models.Model):
   _name = 'idea.management'
   _description = 'Idea'
   _inherit = ['mail.thread.cc',
               'mail.thread.blacklist',
               'mail.activity.mixin']
   _primary_email = 'email_from'
   vote_ids = fields.One2many('idea.management.vote', 'idea_id', string='Votes', help="Votos de los empleados.")

   name = fields.Char(string = 'Propuesta', required=True, help = 'Esto es el nombre de la propuesta / idea')
   create_date = fields.Date(string = 'Fecha de creación', default=_date_default_today, help = 'Fecha de creación')
   deadline = fields.Date(string = 'Fecha límite', help = 'Fecha de finalización')
   idea_type = fields.Selection(
      [('mejoras', 'Mejoras'),
      ('proyecto', 'Plantear proyecto'),
      ('otros', 'Otros'),], 
      string="Tipo de idea")
   
   details = fields.Text(help = 'Descripción de la idea')
   price = fields.Float(string="Coste estimado", help = 'Coste estimado de la idea')
   state = fields.Selection(
      [('revision', 'En revision'), 
      ('aprobada','Aprobada'),
      ('proceso', 'En proceso'),
      ('completada', 'Completada'),
      ('cancelada', 'Cancelada')],
      string = 'Estado',
      default = 'revision')
   
   assigned = fields.Boolean(string = 'Assigned', compute='_compute_assigned')

   partner_id = fields.Many2one(comodel_name='res.partner', string='Compañía', compute='_compute_compañia', store=True, help = 'Compañía')
   employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado', help="Empleado que ha tenido la idea.")
   email_from = fields.Char(string='Email from')
   voter_id = fields.Many2one('hr.employee', string='Empleado que vota', help="Empleado que ha votado la idea.")
   
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

   # Comprobación de que el coste no puede ser negativo.
   @api.constrains('price')
   def _price_positive(self):
      if self.price < 0:
            raise ValidationError(_("El coste no puede ser negativo."))

   # Comprobación de que la fecha límite no puede ser anterior a la fecha actual.
   @api.constrains('deadline')
   def _check_deadline(self):
      for record in self:
         if record.deadline and record.deadline < fields.Date.today():
            raise ValidationError("La fecha límite no puede ser anterior a la fecha actual.")

   # Automáticamente te suma 5 días a la fecha actual (en caso de querer poner la fecha límite a mano también puedes cambiarla desde el formulario).
   @api.onchange('create_date')
   def _update_deadline(self):
      if self.create_date:
         self.deadline = self.create_date + timedelta(days=5)
   
   def open_vote_form(self):
      view_id = self.env.ref('ideas_module.view_idea_vote_form').id

      return {
         'name': 'Voto del Empleado',
         'view_type': 'form',
         'view_mode': 'form',
         'res_model': 'idea.management.vote',
         'views': [(view_id, 'form')],
         'type': 'ir.actions.act_window',
         'target': 'new',
         'context': {
               'default_idea_id': self.id,
               'default_idea_name': self.name,
         },
      }
   
   @api.depends('employee_id')
   def _compute_assigned(self):
      for record in self:
         record.assigned = self.employee_id and True or False

   ideas_empleado = fields.Integer(string='Número de ideas del empleado', compute='_compute_ideas_employee')

   @api.depends('employee_id')
   def _compute_ideas_employee(self):
      for record in self:
         other_tickets = self.env['idea.management'].search([('employee_id', '=', record.employee_id.id)])
         record.ideas_empleado = len(other_tickets)
      
   @api.depends('employee_id')
   def _compute_compañia(self):
      for record in self:
         if record.employee_id:
               record.partner_id = record.employee_id.company_id.partner_id
         else:
               record.partner_id = False

   # @api.onchange('employee_id')
   # def _onchange_empleado(self):
   #    if self.employee_id:
   #       self.partner_id = self.employee_id.company_id.partner_id.id
   #    else:
   #       self.partner_id = False