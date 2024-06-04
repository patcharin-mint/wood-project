from flask import Blueprint, Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from . import db # =  from __init__.py import db
from .service.manageService import RoleForm, WoodForm, SourceForm 
from .models import Role, Wood, Source
from flask_login import current_user




manage_blueprint = Blueprint('manage_blueprint', __name__)


@manage_blueprint.route('/manage', methods=['GET', 'POST'])
def manage_all():
    role_form = RoleForm(prefix='role')
    wood_form = WoodForm(prefix='wood')
    source_form = SourceForm(prefix='source')
    
    roles = Role.query.all()
    woods = Wood.query.all()
    sources = Source.query.all()

    if role_form.validate_on_submit() and role_form.submit.data:
        new_role = Role(role_name=role_form.role_name.data)
        db.session.add(new_role)
        db.session.commit()
        return redirect(url_for('manage_blueprint.manage_all'))

    if wood_form.validate_on_submit() and wood_form.submit.data:
        new_wood = Wood(wood_name=wood_form.wood_name.data, wood_nickname=wood_form.wood_nickname.data)
        db.session.add(new_wood)
        db.session.commit()
        return redirect(url_for('manage_blueprint.manage_all'))

    if source_form.validate_on_submit() and source_form.submit.data:
        new_source = Source(source_name=source_form.source_name.data)
        db.session.add(new_source)
        db.session.commit()
        return redirect(url_for('manage_blueprint.manage_all'))

    return render_template('manage_all.html', role_form=role_form, wood_form=wood_form, source_form=source_form, roles=roles, woods=woods, sources=sources, user=current_user)



@manage_blueprint.route('/edit/<string:type>/<int:id>', methods=['GET', 'POST'])
def edit_item(type, id):
    if type == 'role':
        item = Role.query.get_or_404(id)
        form = RoleForm(obj=item, prefix='role')
    elif type == 'wood':
        item = Wood.query.get_or_404(id)
        form = WoodForm(obj=item, prefix='wood')
    elif type == 'source':
        item = Source.query.get_or_404(id)
        form = SourceForm(obj=item, prefix='source')
    else:
        return redirect(url_for('manage_blueprint.manage_all'))

    if form.validate_on_submit():
        if type == 'role':
            item.role_name = form.role_name.data
        elif type == 'wood':
            item.wood_name = form.wood_name.data
            item.wood_nickname = form.wood_nickname.data
        elif type == 'source':
            item.source_name = form.source_name.data
        db.session.commit()
        return redirect(url_for('manage_blueprint.manage_all'))
    
    return render_template('edit_item.html', form=form, type=type, user=current_user)



@manage_blueprint.route('/dashboard')
def dashboard():
    roles = Role.query.all()
    woods = Wood.query.all()
    return render_template('dashboard.html', roles=roles, woods=woods, user=current_user)