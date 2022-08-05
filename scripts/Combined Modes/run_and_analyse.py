import sys

from clovars.main import main as clovars_main


def main() -> None:
    """Main function of this script."""
    sys.argv = [sys.argv[0], 'run', 'run.toml', 'colonies.toml']
    clovars_main()
    sys.argv = [sys.argv[0], 'analyse', 'analysis.toml']
    clovars_main()


if __name__ == '__main__':
    main()
