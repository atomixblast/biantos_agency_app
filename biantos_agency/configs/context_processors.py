from biantos_agency.utilities import ui_consts



def base_template(request):
    return {
        'base': 'base_htmx.html'
        if request.headers.get('HX-Request', False)
        else 'base.html',
        'ui_consts': ui_consts,
    }

def ui_class(request):
    return {'ui_consts': ui_consts}