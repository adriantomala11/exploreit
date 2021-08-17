<h1>Explore It</h1>
<p>This project was generated with <a href="https://github.com/django/django">Django</a> version 3.1.4</p>
<p>The requirements for this project are on <a href="./requirements.txt">requirements.txt</a></p>

<h2>Installation</h2>
<p>Run <code>pip install -r requirements.txt</code> to install requirements to run the program.</p>
<p>Run <code>python manage.py makemigrations</code> to prepare the necessary migrations to generate the tables.</p>
<p>Run <code>python manage.py migrate</code> to do the migrations defined on the project.</p>
<p>Run <code>python manage.py createsuperuser</code> to create a super user to sign in on django admin.</p>

<h2>Development Server</h2>
<p>Run <code>python manage.py runserver</code> to do the migrations defined on the project.</p>


<h2>Running unit tests</h2>

<p>Django’s unit tests use a Python standard library module: <a href="https://docs.python.org/3/library/unittest.html#module-unittest">unittest</a>.</p>
<p>This project uses <a href="https://docs.djangoproject.com/en/3.2/topics/testing/tools/#django.test.TestCase">TestCase</a>, which is a subclass of unittest. That runs each test inside a transaction to provide isolation without affecting the real database that is used on Production or on development.</p>
<p>Use <code>python manage.py test</code> to execute all tests. </p>

<p>Use <code>python manage.py test main_app</code> to execute all tests of the main module.</p>

<p>Use <code>python manage.py test admin_app</code> to execute all tests of the admin module.</p>
<h2>Tools from Software 2</h2>
<p>Application profiling - CProfile</p>
<p>To install: <code>pip install django-cprofile-middleware</code></p>

<p>Continuous integration: Jenkins</p>
<p>Acceptance testing: Behave</p>
