from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('发表成功！')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('/index.html', title='主页', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(userName=form.userName.data).first()
        if user is None or not user.check_userPwd(form.userPwd.data):
            flash('Invalid userName or userPwd')
            return redirect(url_for('login'))
        login_user(user, remember=form.rememberMe.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='登录', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(userName=form.userName.data, phone=form.phone.data)
        user.set_userPwd(form.userPwd.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(userName=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('user', username=user.userName, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.userName, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.userName = form.userName.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('user', username=current_user.userName))
    elif request.method == 'GET':
        form.userName.data = current_user.userName
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='修改个人信息', form=form)


@app.route('/follow/<userName>')
@login_required
def follow(userName):
    user = User.query.filter_by(userName=userName).first()
    if user is None:
        flash('用户{}未找到！'.format(userName))
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能关注你自己！')
        return redirect(url_for('user', userName=userName))
    current_user.follow(user)
    db.session.commit()
    flash('成功关注{}'.format(userName))
    return redirect(url_for('user', username=userName))


@app.route('/unfollow/<userName>')
@login_required
def unfollow(userName):
    user = User.query.filter_by(userName=userName).first()
    if user is None:
        flash('用户{}未找到！'.format(userName))
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能取关你自己！')
        return redirect(url_for('user', userName=userName))
    current_user.unfollow(user)
    db.session.commit()
    flash('取关{}成功！'.format(userName))
    return redirect(url_for('user', username=userName))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='探索', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
