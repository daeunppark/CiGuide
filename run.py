#!/usr/bin/env python3
"""CiGuide launcher: CLI, filtering tree, evaluation, or synchronized build."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
if len(sys.argv)>1 and sys.argv[1] in ('evaluate','build'):
    import argparse,json
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['evaluate','build'])
    parser.add_argument('--trials',type=int,default=10000)
    parser.add_argument('--seed',type=int,default=6903)
    args=parser.parse_args()
    if args.command=='build':
        if args.trials!=10000 or args.seed!=6903:parser.error('build uses the default reproducible experiment')
        from build_assets import build
        print(json.dumps(build(),indent=2))
    else:
        if args.trials<1:parser.error('trials must be positive')
        from evaluate import experiment
        result=experiment(args.trials,args.seed)
        target=Path(__file__).resolve().parent/'reports/evaluation_results.json'
        target.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
else:
    from decision_engine import main
    main()
