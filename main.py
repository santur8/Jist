from result import Err
from factories import AppFactory
import click
import json


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="path to job config",
)
def main(config: str):
    with open(config, "r") as f:
        app = AppFactory.new(json.load(f))
        print(app.execute())


if __name__ == "__main__":
    main()
