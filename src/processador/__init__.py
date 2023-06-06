from .processador import Processador
from .procauxacidente import ProcessadorAuxAcidente
from .procauxincap import ProcessadorAuxIncapacidade
from .procbpcidoso import ProcessadorBenAssIdoso
from .prociir import ProcessadorIsencaoIR
from .procmaj import ProcessadorMajoracao25
from .procprosalmat import ProcessadorProrrogSalMaternidade
from .procsm import ProcessadorSalMaternidade

__all__ = ["Processador", "ProcessadorAuxAcidente", "ProcessadorAuxIncapacidade", 
           "ProcessadorBenAssIdoso", "ProcessadorIsencaoIR", "ProcessadorMajoracao25",
            "ProcessadorProrrogSalMaternidade", "ProcessadorSalMaternidade"]