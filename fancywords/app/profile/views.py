from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import profile
from .. import db
from .forms import UpdateAccountForm
from .utils import save_picture


@profile.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pictures')
            current_user.avatar_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('profile.account'))
    form.username.data = current_user.username
    form.email.data = current_user.email
    image_file = url_for('static',
                     filename='profile_pictures/' + current_user.avatar_file)
    return render_template('profile/account.html', title='Account',
                           image_file=image_file, form=form)
