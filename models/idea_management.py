from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

def _date_default_today(self):
   return fields.Date.today() # Para que nos devuelva el día actual en el que estamos.

class IdeaManagementVote(models.Model):
   _name = 'idea.management.vote'
   _description = 'Idea Management Vote'

   rating = fields.Selection(
      [('0', 'Very Low'), ('1', 'Baja'), ('2', 'Normal'), ('3', 'Alto'), ('4', 'Muy alto'), ('5', 'Excelente')],
      string="Valoraciones")
   comments = fields.Char(string="Comentarios")
   user_id = fields.Many2one(comodel_name='res.users', string='Empleados')
   idea_id = fields.Many2one('idea.management', string='Nombre de la idea', readonly=True)
   
   def save_vote(self):
    self.ensure_one()
    # Busca si ya existe un voto para este usuario en esta idea
    existing_vote = self.idea_id.vote_ids.filtered(lambda v: v.user_id == self.user_id)
    if existing_vote:
        # Si ya existe, actualiza el voto existente
        existing_vote.write({
            'rating': self.rating,
            'comments': self.comments,
        })
        return {'type': 'ir.actions.act_window_close'}  # Cierra la ventana después de actualizar el voto existente
    else:
        # Si no existe, no hace nada
        return {'type': 'ir.actions.act_window_close'}

   
class IdeaManagement(models.Model):
   _name = 'idea.management'
   _description = 'Idea'
   _inherit = ['mail.thread.cc',
               'mail.thread.blacklist',
               'mail.activity.mixin']
   _primary_email = 'email_from'
   vote_ids = fields.One2many('idea.management.vote', 'idea_id', string='Votes')

   name = fields.Char(string = 'Propuesta')
   create_date = fields.Date(string = 'Fecha de creación', default=_date_default_today)
   deadline = fields.Date(string = 'Fecha límite')
   idea_type = fields.Selection(
      [('mejoras', 'Mejoras'),
      ('proyecto', 'Plantear proyecto'),
      ('otros', 'Otros'),], 
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
   email_from = fields.Char(string='Email from')
   voter_id = fields.Many2one('res.users', string='Usuario que vota')
   
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
        'name': 'Voto del Usuario',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'idea.management.vote',
        'views': [(view_id, 'form')],
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': {
            'default_idea_id': self.id,
            'default_idea_name': self.name,
        }
    }