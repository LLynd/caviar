import click
import typing

PenetrationListValue = typing.List[list]


class PenListParamType(click.ParamType):
    name = 'penetration_list'

    def convert(self, value: str, param: click.Parameter, ctx: click.Context) -> PenetrationListValue:
     
        value = value.translate({ord('['): None})
        value = value.translate({ord(']'): None})

        tmp = value.split(',')
        
        if len(tmp) < 2:
            self._notEnoughArguments(value, param, ctx)
        
        try:
            penetration_list = [float(element) for element in tmp]
            return penetration_list
        except ValueError:
            self._invalidFormat(value, param, ctx)
            
            
    def _notEnoughArguments(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
         self.fail(
            f'expected at least two penetration rates to run an experiment, got "{value}" instead',
            param,
            ctx,
        )

    def _invalidFormat(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
        self.fail(
            f'expected list of floats and valid intigers divided by a comma, f.e. [0.1,0.2] or 0.1,0.2, got penetration-list = "{value}". \n' 
            f'Try: typing without any blank spaces',
            param,
            ctx,
        )