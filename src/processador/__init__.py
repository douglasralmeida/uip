from .processador import Processador
from .procauxacidente import ProcessadorAuxAcidente
from .procauxincap import ProcessadorAuxIncapacidade
from .procben import ProcessadorBeneficio
from .procbpcdef import ProcessadorBenAssDeficiente
from .procbpcidoso import ProcessadorBenAssIdoso
from .prociir import ProcessadorIsencaoIR
from .procmaj import ProcessadorMajoracao25
from .procprosalmat import ProcessadorProrrogSalMaternidade
from .procsd import ProcessadorSeguroDefeso
from .procsm import ProcessadorSalMaternidade

__all__ = ["Processador", "ProcessadorAuxAcidente", "ProcessadorAuxIncapacidade", 
           "ProcessadorBenAssDeficiente", "ProcessadorBeneficio", "ProcessadorBenAssIdoso", "ProcessadorIsencaoIR",
            "ProcessadorMajoracao25", "ProcessadorProrrogSalMaternidade", "ProcessadorSeguroDefeso", "ProcessadorSalMaternidade"]