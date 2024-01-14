from odoo import models, fields, api
from odoo.exceptions import ValidationError

import secrets


class Product(models.Model):
    _name = 'product_model'

    name = fields.Char(required=True, string='Название товара')
    manufacturer = fields.Char(string='Производитель')
    description = fields.Text(string='Описание товара')
    
class Stock(models.Model):
    _name = 'stock_model'

    name = fields.Char(required=True, string='Название склада')
    addresses = fields.Text(string='Адрес склада')
    
class Costs_income(models.Model):
    _name = 'costs_income_model'

    date = fields.Date(default=fields.Date.context_today, readonly=True)
    name = fields.Char(required=True, string='Название затраты/прихода')
    currency_id = fields.Many2one('res.currency', string="Валюта",
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)
    value = fields.Monetary(string='Значение')
    act_id = fields.Many2one(comodel_name='act_model')
    product_lebeling_id = fields.Many2many(comodel_name='product_lebeling_model')

class Act_change_properties(models.Model):
    _name = 'act_model'
    
    application = fields.Boolean(readonly=True, default=False, string="Акт применен")
    date = fields.Date(default=fields.Date.context_today, string='Дата', readonly=True)
    state = fields.Selection(selection = [('Покупка', 'Покупка'), ('Продажа', 'Продажа'), ('Перемещение', 'Перемещение'), ('Списание', 'Списание')], string='Назначаемый статус')
    stock_first = fields.Many2one(comodel_name='stock_model', string='Применить для товаров со склада')
    stock_second = fields.Many2one(comodel_name='stock_model', string='Назначить новый склад')
    product = fields.Many2one(comodel_name='product_model', string='Товар')
    count = fields.Integer(default=1, string='Количество')
    costs_income = fields.One2many(comodel_name='costs_income_model', inverse_name='act_id', string='Сводка')
    
    def application_act(self):
        if self.application == False:
           if self.state == 'Покупка':
                costs_income = self.costs_income
                for el in range(self.count):
                        record = self.env['product_lebeling_model'].create([{'product': self.product.id, 'stock': self.stock_second.id, 'state': self.state, 'costs_income': costs_income}])
                        if not costs_income:  
                            costs = self.env['costs_income_model'].search([('name', '=', "Покупка"), ('act_id', '=', self.id)])
                            if not costs:   
                                self.env['costs_income_model'].create([{'name': "Покупка", 'act_id': self.id, 'product_lebeling_id': record}])
                            else:
                                record.costs_income += costs
                        record.costs_income += costs_income
                self.application = True
                return
           if self.state == 'Перемещение':
               records = self.env['product_lebeling_model'].search([('stock', '=', self.stock_first.name), ('product', '=', self.product.name), ('state', '!=', 'Продажа'), ('state', '!=', 'Списание')])
               if len(records) >= self.count:
                   for el in range(self.count):
                       costs = self.env['costs_income_model'].search([('name', '=', f"{self.state} со склада {self.stock_first}"), ('act_id', '=', self.id)])
                       if not costs:
                            self.env['costs_income_model'].create([{'name': f"{self.state} со склада {self.stock_first}", 'act_id': self.id, 'product_lebeling_id': records[el]}])
                       else:
                           costs.product_lebeling_id += records[el]
                       records[el].write({'stock': self.stock_second.id, 'state': self.state})
                       records[el].costs_income += self.costs_income
                   self.application = True
                   return
               raise ValidationError("На указанном складе отсутствует указанное количество товара. Применение акта невозможно")
           if self.state == 'Списание':
               records = self.env['product_lebeling_model'].search([('stock', '=', self.stock_first.name), ('product', '=', self.product.name), ('state', '!=', 'Продажа'), ('state', '!=', 'Списание')])
               if len(records) >= self.count:
                   for el in range(self.count):
                       costs = self.env['costs_income_model'].search([('name', '=', f"{self.state} со склада {self.stock_first}"), ('act_id', '=', self.id)])
                       if not costs:
                            self.env['costs_income_model'].create([{'name': f"{self.state} со склада {self.stock_first}", 'act_id': self.id, 'product_lebeling_id': records[el]}])
                       else:
                           costs.product_lebeling_id += records[el]
                       records[el].write({'state': self.state})
                       records[el].costs_income += self.costs_income
                   self.application = True
                   return
               raise ValidationError("На указанном складе отсутствует указанное количество товара. Применение акта невозможно")
           if self.state == 'Продажа':
               records = self.env['product_lebeling_model'].search([('stock', '=', self.stock_first.name), ('product', '=', self.product.name), ('state', '!=', 'Продажа'), ('state', '!=', 'Списание')])
               if len(records) >= self.count:
                   for el in range(self.count):
                       costs = self.env['costs_income_model'].search([('name', '=', f"{self.state} со склада {self.stock_first}"), ('act_id', '=', self.id)])
                       if not costs:
                            self.env['costs_income_model'].create([{'name': f"{self.state} со склада {self.stock_first}", 'act_id': self.id, 'product_lebeling_id': records[el]}])
                       else:
                           costs.product_lebeling_id += records[el]
                       records[el].write({'state': self.state})
                       records[el].costs_income += self.costs_income
                   self.application = True
                   return
               raise ValidationError("На указанном складе отсутствует указанное количество товара. Применение акта невозможно")
        else:
            raise ValidationError("Акт уже применен. Повторное применение невозможно")
 
def generate_code(*args, **kwargs):
    return secrets.token_hex(11)

class Product_lebeling(models.Model):
    _name = 'product_lebeling_model'
    _order = "id desc"
    
    code = fields.Char(default=generate_code, unique=True, string='Уникальный код', readonly=True)
    product = fields.Many2one(comodel_name='product_model', string='Товар', readonly=True)
    stock = fields.Many2one(comodel_name='stock_model', string='Последний назначенный склад', readonly=True)
    state = fields.Char(string='Последний назначенный статус', readonly=True)
    costs_income = fields.Many2many(comodel_name='costs_income_model', string='Сводка', readonly=True)
    total = fields.Float(compute='_compute_total', string='Итого')
    
    @api.depends()
    def _compute_total(self):
        eln = self.env['costs_income_model'].search([('product_lebeling_id', '=', self.id)])
        for el in eln:
            self.total += el.value
    

    