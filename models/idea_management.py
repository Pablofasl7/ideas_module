from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import base64

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.  
   
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
   
   # Esto es un campo calculado para los días entre la fecha de creación y la fecha límite (para mostrar en la vista calendario).
   days_duration = fields.Integer(compute='_compute_days_duration', string='Duración (días): ', store=True)

   idea_type = fields.Selection(
      [('mejoras', 'Mejoras'),
      ('proyecto', 'Plantear proyecto'),
      ('otros', 'Otros'),], 
      string="Tipo de idea",
      default="otros")
   
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
   
   active = fields.Boolean(string='Activo', default=True, help = 'Para archivar la idea.')
   archive_cancelled = fields.Boolean(compute='_compute_archive_cancelled', store=True)
   
   assigned = fields.Boolean(string = 'Assigned', compute='_compute_assigned')

   partner_id = fields.Many2one(comodel_name='res.partner', string='Compañía', compute='_compute_compañia', store=True, help = 'Compañía')
   employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado', help="Empleado que ha tenido la idea.")
   email_from = fields.Char(string='Email from')
   voter_id = fields.Many2one('hr.employee', string='Empleado que vota', help="Empleado que ha votado la idea.")

   # Para poder mostrar la cantidad de ideas por estado en la vista graph.
   revision_count = fields.Integer(string="En Revisión", compute='_compute_state_counts', store=True)
   aprobada_count = fields.Integer(string="Aprobadas", compute='_compute_state_counts', store=True)
   proceso_count = fields.Integer(string="En Proceso", compute='_compute_state_counts', store=True)
   completada_count = fields.Integer(string="Completadas", compute='_compute_state_counts', store=True)
   cancelada_count = fields.Integer(string="Canceladas", compute='_compute_state_counts', store=True)
   
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

   # Comprobamos que la fecha límite no sea anterior a la fecha actual. Y en ese caso establecemos la idea en completada.
   @api.depends('deadline')
   def _check_deadline_expired(self):
      for record in self:
         if record.deadline and record.deadline < fields.Date.today():
               record.state = 'completada'

   @api.depends('create_date', 'deadline')
   def _compute_days_duration(self):
      for idea in self:
         if idea.create_date and idea.deadline:
               duration = (idea.deadline - idea.create_date).days
               idea.days_duration = duration if duration >= 0 else 0
         else:
               idea.days_duration = 0            
   
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
               'default_employee_id': self.env.user.employee_id.id,
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

   @api.depends('state')
   def _compute_state_counts(self):
      self.revision_count = len(self.filtered(lambda r: r.state == 'revision'))
      self.aprobada_count = len(self.filtered(lambda r: r.state == 'aprobada'))
      self.proceso_count = len(self.filtered(lambda r: r.state == 'proceso'))
      self.completada_count = len(self.filtered(lambda r: r.state == 'completada'))
      self.cancelada_count = len(self.filtered(lambda r: r.state == 'cancelada'))

   def change_state(self):
        for idea in self:
            if idea.state == 'revision':
                idea.state = 'aprobada'
            elif idea.state == 'aprobada':
                idea.state = 'proceso'
            elif idea.state == 'proceso':
                idea.state = 'completada'

   @api.depends('state', 'active')
   def _compute_archive_cancelled(self):
      for idea in self:
         if idea.state == 'cancelada' and idea.active:
               idea._archive_idea()

   def _archive_idea(self):
    for idea in self:
        idea.active = False

   # def action_idea_send_by_email(self):
   #      self.ensure_one()
   #      ctx = {
   #          'default_model': 'idea.management',
   #          'default_res_ids': self.ids,
   #          'default_composition_mode': 'comment',
   #          'mark_so_as_sent': True,
   #          'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
   #          'proforma': self.env.context.get('proforma', False),
   #          'force_email': True,
   #      }
   #      return {
   #          'type': 'ir.actions.act_window',
   #          'view_mode': 'form',
   #          'res_model': 'mail.compose.message',
   #          'views': [(False, 'form')],
   #          'view_id': False,
   #          'target': 'new',
   #          'context': ctx,
   #      }