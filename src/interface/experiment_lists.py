import click
import typing

PenetrationListValue = typing.List[list]
DispatchListValue = typing.List[list]
EmergencyListValue = typing.List[list]


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


class DisListParamType(click.ParamType):
    name = 'dispatch_list'

    def convert(self, value: str, param: click.Parameter, ctx: click.Context) -> DispatchListValue:
     
        value = value.translate({ord('['): None})
        value = value.translate({ord(']'): None})

        tmp = value.split(',')
        
        if len(tmp) < 1:
            self._notEnoughArguments(value, param, ctx)
        
        try:
            dispatch_list = [int(element) for element in tmp]
            return dispatch_list
        except ValueError:
            self._invalidFormat(value, param, ctx)
            
            
    def _notEnoughArguments(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
         self.fail(
            f'expected at least one dispatch value to run an experiment, got "{value}" instead',
            param,
            ctx,
        )

    def _invalidFormat(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
        self.fail(
            f'expected list of intigers divided by a comma, f.e. [2,4] or 2,4, got dispatch-list = "{value}". \n' 
            f'Try: typing without any blank spaces',
            param,
            ctx,
        )


class EmergListParamType(click.ParamType):
    name = 'emergency_list'

    def convert(self, value: str, param: click.Parameter, ctx: click.Context) -> EmergencyListValue:
     
        value = value.translate({ord('['): None})
        value = value.translate({ord(']'): None})

        tmp = value.split(',')
        
        if len(tmp) < 1:
            self._notEnoughArguments(value, param, ctx)
        
        try:
            emergency_list = [int(element) for element in tmp]
            return emergency_list
        except ValueError:
            self._invalidFormat(value, param, ctx)
            
            
    def _notEnoughArguments(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
         self.fail(
            f'expected at least emergency dispatch value to run an experiment, got "{value}" instead',
            param,
            ctx,
        )

    def _invalidFormat(self, value: str, param: click.Parameter, ctx: click.Context) -> None:
        self.fail(
            f'expected list of intigers divided by a comma, f.e. [200,400] or 200,400, got dispatch-list = "{value}". \n' 
            f'Try: typing without any blank spaces',
            param,
            ctx,
        )