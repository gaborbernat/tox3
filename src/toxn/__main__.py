"""main entry point for running toxn"""
import sys

from toxn.evaluate import main

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
