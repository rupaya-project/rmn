import sys
import click
from tmn import __version__
from tmn import display
from tmn import masternode
from tmn import configuration

conf = None


@click.group(help='Tomo MasterNode (tmn) is a cli tool to help you run a '
             + 'Tomochain masternode')
@click.option('--dockerurl',
              metavar='URL',
              help='Url to the docker server')
@click.version_option(version=__version__)
def main(dockerurl):
    """
    Cli entrypoint.

    :param config: path to the configuration file
    :type config: str
    """
    if not masternode.connect(url=dockerurl):
        display.error_docker()
        sys.exit()


@click.command(help='Display Tomochain documentation link')
def docs():
    """
    Link to the documentation

    :param open: open the link in your navigator
    :type open: bool
    """
    display.link_docs()


@click.command(help='Start your Tomochain masternode')
@click.option('--name',
              metavar='NAME',
              help='Your masternode\'s name')
def start(name):
    """
    Start the containers needed to run a masternode
    """
    configuration.init(name)
    display.title_start_masternode()
    masternode.start(configuration.name)


@click.command(help='Stop your Tomochain masternode')
def stop():
    """
    Stop the containers needed to run a masternode
    """
    configuration.init()
    display.title_stop_masternode()
    masternode.stop(configuration.name)


@click.command(help='Status of your Tomochain masternode')
def status():
    """
    Display the status of the masternode containers
    """
    configuration.init()
    display.title_status_masternode()
    masternode.status(configuration.name)


main.add_command(docs)
main.add_command(start)
main.add_command(stop)
main.add_command(status)
