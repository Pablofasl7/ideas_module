from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class IdeaManagementVote(models.Model):
   _name = 'idea.management.vote'
   _description = 'Idea Management Vote'

   rating = fields.Selection(
      [('0', 'Very Low'), ('1', 'Baja'), ('2', 'Normal'), ('3', 'Alto'), ('4', 'Muy alto'), ('5', 'Excelente')],
      string="Valoraciones")
   comments = fields.Char(string="Comentarios", help="Aquí puedes dejar comentarios que leerán tanto los administradores como los demás usuarios (por ejemplo para mejorar la idea).")
   employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado', help="El empleado que ha votado la idea.")
   idea_id = fields.Many2one('idea.management', string='Nombre de la idea', readonly=True, help="La idea que ha votado.")
   
   registered_votes = []

   def save_vote(self):
        for vote in self:
            existing_vote = next((v for v in self.registered_votes if v['idea_id'] == vote.idea_id.id and v['employee_id'] == vote.employee_id.id), None)
            if not existing_vote:
                self.env['idea.management.vote'].write({
                    'employee_id': vote.employee_id.id,
                    'rating': vote.rating,
                    'comments': vote.comments,
                    'idea_id': vote.idea_id.id,
                })
                self.registered_votes.append({
                    'employee_id': vote.employee_id.id,
                    'idea_id': vote.idea_id.id,
                })
            else:
                raise ValidationError("No puedes votar dos veces la misma idea.")
               

   # Obtenemos el voto del empleado actual y si le damos al botón cancelar, no guardamos el boto (lo eliminamos)
   def cancel_vote(self):
      id_vote = self.env.context.get('active_id')  
      if id_vote:
         idea_record = self.env['idea.management'].browse(id_vote) 
         if idea_record:
            last_vote = idea_record.vote_ids[-1] 
            last_vote.unlink()