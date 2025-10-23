class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    remetente = db.Column(db.String(320), index=True)
    destinatario = db.Column(db.String(320), index=True)
    assunto = db.Column(db.String(70), index=True)
    corpo = db.Column(db.String(320), index=True)
    data = db.Column(db.String(21), index=True)

def send_simple_message(to, subject, newUser):
    print('Enviando mensagem (POST)...', flush=True)
    print('URL: ' + str(app.config['API_URL']), flush=True)
    print('api: ' + str(app.config['API_KEY']), flush=True)
    print('from: ' + str(app.config['API_FROM']), flush=True)
    print('to: ' + str(to), flush=True)
    print('subject: ' + str(app.config['FLASKY_MAIL_SUBJECT_PREFIX']) + ' ' + subject, flush=True)
    print('text: ' + "Prontuário: PT3025993\nNome: Lais Gabriele Da Silva\nNovo usuário cadastrado: " + newUser, flush=True)

    resposta = requests.post(app.config['API_URL'], 
                             auth=("api", app.config['API_KEY']), data={"from": app.config['API_FROM'], 
                                                                        "to": to, 
                                                                        "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, 
                                                                        "text": "Prontuário: PT3025993\nNome: Lais Gabriele Da Silva \nNovo usuário cadastrado: " + newUser})
    print('Enviando mensagem (Resposta)...' + str(resposta) + ' - ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True)
    email = Email(remetente = newUser, destinatario = str(to), assunto = str(app.config['FLASKY_MAIL_SUBJECT_PREFIX']) + ' ' + subject, corpo = "Prontuário: PT303304X\nNome: Giovanna Karolline Menezes Ribeiro\nNovo usuário cadastrado: " + newUser, data = datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    db.session.add(email)
    db.session.commit()
    return resposta


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    sendEmail = BooleanField('Deseja enviar e-mail para flaskaulasweb@zohomail.com?')
    submit = SubmitField('Submit')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/emailsEnviados')
def emailsEnviados():
    emails = Email.query.all()
    return render_template('emailsEnviados.html', emails = emails)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data, role = Role.query.filter_by(name="User").first())
            mandarEmail = form.sendEmail.data
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            
            print('Verificando variáveis de ambiente: Server log do PythonAnyWhere', flush=True)
            print('FLASKY_ADMIN: ' + str(app.config['FLASKY_ADMIN']), flush=True)
            print('URL: ' + str(app.config['API_URL']), flush=True)
            print('api: ' + str(app.config['API_KEY']), flush=True)
            print('from: ' + str(app.config['API_FROM']), flush=True)
            print('to: ' + str([app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com"]), flush=True)
            print('subject: ' + str(app.config['FLASKY_MAIL_SUBJECT_PREFIX']), flush=True)
            print('text: ' + "Prontuário: PT3025993\nNome: Lais Gabriele Da Silva\nNovo usuário cadastrado: " + form.name.data, flush=True)

            if app.config['FLASKY_ADMIN'] and mandarEmail:                
                print('Enviando mensagem...', flush=True)
                send_simple_message([app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com"], 'Novo usuário', form.name.data)
                print('Mensagem enviada...', flush=True)
            elif app.config['FLASKY_ADMIN']:
                print('Enviando mensagem...', flush=True)
                send_simple_message([app.config['FLASKY_ADMIN']], 'Novo usuário', form.name.data)
                print('Mensagem enviada...', flush=True)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False), usuarios=User.query.all(), funcoes=Role.query.all())
