import nox


@nox.session(reuse_venv=True)
def lint(session):
    session.install('.[lint]')
    session.run('flake8', '-v', 'playground_plums')
    session.run('flake8', '-v', '--ignore=D', 'tests')


@nox.session(python=['3.6', '3.7', '3.8', '3.9'], reuse_venv=True)
def tests(session):
    session.install('.[tests]')
    session.run('pytest', '-vv', '--cov-report', 'term-missing', '--cov=playground_plums', '--ignore=tests/test_dataflow', 'tests/')
    session.run('pytest', '-vv', '--cov-report', 'term-missing', '--cov=playground_plums', 'tests/test_dataflow')
