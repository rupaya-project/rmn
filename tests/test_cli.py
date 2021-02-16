import pytest

import docker

import rupayamn as package

client = docker.from_env()


@pytest.fixture
def runner():
    from click.testing import CliRunner
    runner = CliRunner()
    return runner


@pytest.fixture
def rupayamn():
    from rupayamn import rupayamn
    from rupayamn.environments import environments
    from rupayamn import configuration
    environments['devnet'] = {
        'rupaya': {
            'BOOTNODES': (
                'test'
            ),
            'NETSTATS_HOST': 'test.com',
            'NETSTATS_PORT': '443',
            'NETWORK_ID': '90',
            'WS_SECRET': (
                'test'
            )
        },
        'metrics': {
            'METRICS_ENDPOINT': 'https://test.com'
        }
    }
    environments['testnet'] = environments['devnet']
    configuration.resources.init('rupaya', 'rupaya_tests')
    return rupayamn


def _clean(rupayamn):
    from rupayamn import configuration
    try:
        client.containers.get('test1_rupaya').remove(force=True)
    except Exception:
        pass
    try:
        client.containers.get('test1_metrics').remove(force=True)
    except Exception:
        pass
    try:
        client.volumes.get('test1_chaindata').remove(force=True)
    except Exception:
        pass
    try:
        client.networks.get('test1_rupayamn').remove()
    except Exception:
        pass
    configuration.resources.init('rupaya', 'rupaya_tests')
    configuration.resources.user.delete('id')
    configuration.resources.user.delete('name')
    configuration.resources.user.delete('net')


def test_version(runner, rupayamn):
    version = '0.5.1'
    result = runner.invoke(rupayamn.main, ['--version'])
    assert result.output[-6:-1] == version
    assert package.__version__ == version


def test_error_docker(runner, rupayamn):
    result = runner.invoke(rupayamn.main, ['--docker', 'unix://test', 'docs'])
    assert '! error: could not access the docker daemon\nNone\n'
    assert result.exit_code == 0


def test_command(runner, rupayamn):
    result = runner.invoke(rupayamn.main)
    assert result.exit_code == 0


def test_command_docs(runner, rupayamn):
    result = runner.invoke(rupayamn.main, ['docs'])
    msg = 'Documentation on running a masternode:'
    link = 'https://docs.rupx.io/masternode/rupayamn/\n'
    assert result.output == "{} {}".format(msg, link)
    assert result.exit_code == 0


def test_command_start_init_devnet(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_start_init_testnet(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'testnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_start_init_mainnet(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'mainnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_start_init_invalid_name(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'tes', '--net', 'devnet', '--pkey', '1234'])
    lines = result.output.splitlines()
    assert 'error' in lines[1]
    assert '! error: --name is not valid' in lines
    _clean(rupayamn)


def test_command_start_init_no_pkey(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net', 'devnet'])
    lines = result.output.splitlines()
    assert ('! error: --pkey is required when starting a new '
            'masternode') in lines
    _clean(rupayamn)


def test_command_start_init_invalid_pkey_len(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net', 'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890'])
    lines = result.output.splitlines()
    assert '! error: --pkey is not valid' in lines
    _clean(rupayamn)


def test_command_start_init_no_net(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'])
    lines = result.output.splitlines()
    assert '! error: --net is required when starting a new masternode' in lines
    _clean(rupayamn)


def test_command_start_init_no_name(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'])
    lines = result.output.splitlines()
    assert ('! error: --name is required when starting a new '
            'masternode') in lines
    _clean(rupayamn)


def test_command_start(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['start'])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_start_ignore(runner, rupayamn):
    result = runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['start', '--name', 'test'])
    lines = result.output.splitlines()
    assert '! warning: masternode test1 is already configured' in lines
    _clean(rupayamn)


def test_command_stop(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['stop'])
    lines = result.output.splitlines()
    assert 'Stopping masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_status(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['status'])
    lines = result.output.splitlines()
    assert 'Masternode test1 status:' in lines
    _clean(rupayamn)


def test_command_inspect(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['inspect'])
    lines = result.output.splitlines()
    assert 'Masternode test1 details:' in lines
    _clean(rupayamn)


def test_command_update(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['update'])
    lines = result.output.splitlines()
    assert 'Updating masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)


def test_command_remove(runner, rupayamn):
    runner.invoke(rupayamn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(rupayamn.main, ['remove', '--confirm'])
    lines = result.output.splitlines()
    assert 'Removing masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(rupayamn)
