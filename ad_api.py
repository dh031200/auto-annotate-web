import argparse

from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology
from autodistill_yolonas import YOLONAS

def annotate(path, kwargs):
    output_folder=f"./upload/{path}/output"
    base_model = GroundedSAM(ontology=CaptionOntology(kwargs))
    base_model.label(
      input_folder=f"./upload/{path}/input",
      output_folder=output_folder
    )
    print('Annotate finished')
    print(f'result saved in `{output_folder}`')
    
def main(args):
    annotate(args.source, kwargs)
    

class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='source')
    parser.add_argument('-k', '--kwargs', nargs='*', action=ParseKwargs)
    _args = parser.parse_args()
    main(_args)
