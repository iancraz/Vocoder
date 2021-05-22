import numpy as np

glotal_types = ["triangular", "hamming", "square", "exp"]

class ArtificialGlotal:
  def __init__(self) -> None:
      pass

  @staticmethod
  def glotal_triangular(len_block: int, p_coverage=0.1, r1_start=0, r1_stop=3, r2_start=1, r2_stop=0):
    """
    Generardor de pulso glotal con base a una señal triangular no necesariamente simetrica
s
    Args:
        len_block (int): largo del bloque
        p_coverage (float, optional): proporción del bloque que cubre el pulso glotal. Defaults to 0.1.
        r1_start (int, optional): comienzo de rampa 1. Defaults to 0.
        r1_stop (int, optional): Fin de rampa 1. Defaults to 3.
        r2_start (int, optional): comienzo de rampa 2. Defaults to 1.
        r2_stop (int, optional): Fin de rampa 2. Defaults to 0.

    Returns:
        glotal pulse: pulso glotal artificial de duración len_block
    """
    vocoded = np.zeros(len_block)
    ramp_len=int(len_block*p_coverage)//2
    ramp_up = np.linspace(r1_start, r1_stop,ramp_len,endpoint=False)
    ramp_down = np.linspace(r2_start,r2_stop,ramp_len*2)
    ramp = np.hstack((ramp_up, ramp_down))
    vocoded[len(vocoded)//2-ramp_len:len(vocoded)//2+ramp_len*2] = ramp
    return vocoded

  @staticmethod
  def glotal_hamming(len_block:int, p_coverage=0.1):
    """
    Generardor de pulso glotal con base a una ventana de hamming

    Args:
        len_block (int): largo del bloque
        p_coverage (float, optional): [description]. Defaults to 0.1.

    Returns:
        glotal pulse: pulso glotal artificial de duración len_block
    """
    vocoded = np.zeros(len_block)
    len_hamming = int(len_block*p_coverage)
    if len_hamming%2 != 0:
      len_hamming = len_hamming + 1
    vocoded[len(vocoded)//2-len_hamming//2:len(vocoded)//2 + len_hamming//2] = np.hamming(len_hamming)
    return vocoded

  @staticmethod
  def glotal_square(len_block: int, p_coverage=0.1):
    """
    Generardor de pulso glotal con base a una ventana rectangular

    Args:
        len_block (int): largo del bloque
        p_coverage (float, optional): [description]. Defaults to 0.1.

    Returns:
        glotal pulse: pulso glotal artificial de duración len_block
    """
    vocoded = np.zeros(len_block)
    square_len=int(len_block*p_coverage)//2
    vocoded[len(vocoded)//2-square_len:len(vocoded)//2+square_len] = 1
    return vocoded

  @staticmethod
  def glotal_exp_rising(len_block:int, p_coverage=0.1, th= 0.1, amplitude= 1.0):
    """
    Generardor de pulso glotal con base a e^(-alfa*abs(x))

    Args:
        len_block (int): largo del bloque
        p_coverage (float, optional): [description]. Defaults to 0.1.
        th (float, optional): [description]. Defaults to 0.1.
        amplitude (float, optional): [description]. Defaults to 1.0.

    Returns:
        Generardor de pulso glotal con base a una ventana de hamming
    """
    vocoded = np.zeros(len_block)
    alpha = (-2/(p_coverage*len_block)) * np.log(th/amplitude)  
    t = np.arange(-len_block//2, len_block//2)
    vocoded = amplitude * np.exp(-alpha * np.abs(t))
    return vocoded