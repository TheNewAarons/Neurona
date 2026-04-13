# neurona_lif.py
import math
from collections import deque

class LIFNeuron:
    """
    Modelo Leaky Integrate-and-Fire (LIF) mejorado con Spike Frequency Adaptation (SFA).
    Simula el comportamiento de una membrana celular neuronal con fatiga biológica.
    """
    def __init__(self, dt=1.0, name="Neuron", v_rest=0.0, v_thresh=1.0, v_reset=-0.2,
                 tau_m=25.0, r_m=1.0, tau_adap=150.0, delta_adap=0.25, t_ref=8.0):
        self.dt = dt
        self.name = name

        # === Parámetros de Membrana ===
        self.v_rest = v_rest            # Potencial de reposo basal
        self.v_thresh = v_thresh        # Umbral mínimo para disparar (Spike)
        self.v_reset = v_reset          # Potencial de reinicio (hiperpolarización post-pico)

        self.tau_m = tau_m              # Constante de tiempo de la membrana (determina el "leak")
        self.r_m = r_m                  # Resistencia de la membrana

        # === Parámetros de Adaptación (SFA) ===
        self.tau_adap = tau_adap        # Constante de tiempo de adaptación
        self.delta_adap = delta_adap    # Incremento de adaptación por spike
        self.I_adap = 0.0               # Corriente de adaptación acumulada

        # === Estado Neuronal ===
        self.v = self.v_rest
        self.t_ref = t_ref              # Período refractario
        self.t_rest = 0.0               # Tiempo restante de refractividad

        # === Estadísticas ===
        self.spike_count = 0
        self.t_last_spike = -1000.0     # Tiempo del último spike (en ms)
        self.t_current = 0.0            # Tiempo de simulación actual
        self.isi_history = deque(maxlen=10)  # Últimos 10 ISIs (inter-spike intervals)
        self.firing_rate = 0.0          # Tasa de disparo en Hz

        self.has_spiked = False
        self.membrane_history = deque([self.v_rest] * 400, maxlen=400)

    def get_voltage(self):
        return self.v

    def get_adaptation(self):
        return self.I_adap

    def reset(self):
        """Resetea completamente la neurona al estado de reposo."""
        self.v = self.v_rest
        self.I_adap = 0.0
        self.t_rest = 0.0
        self.t_last_spike = -1000.0
        self.spike_count = 0
        self.isi_history.clear()
        self.firing_rate = 0.0

    def update(self, I_excit, I_inhib=0.0):
        """
        Actualiza el estado interno de la neurona.

        Args:
            I_excit: Corriente excitatoria entrante
            I_inhib: Corriente inhibitoria entrante (se resta)

        Returns:
            True si la neurona disparó un potencial de acción en este ciclo.
        """
        self.has_spiked = False
        self.t_current += self.dt

        # 1. Evolución de la corriente de adaptación (SFA)
        # dI_adap/dt = -I_adap / tau_adap
        dI_adap = -self.I_adap / self.tau_adap
        self.I_adap += dI_adap * self.dt

        # 2. Chequear si estamos en período refractario
        if self.t_rest > 0:
            self.t_rest -= self.dt
            self.v = self.v_reset
            self._save_history()
            return False

        # 3. Ecuación diferencial del Leaky Integrate and Fire (mejorada)
        # dv/dt = (-(v - v_rest) + R * (I_excit - I_inhib - I_adap)) / tau_m
        I_net = I_excit - I_inhib - self.I_adap
        dv = (-(self.v - self.v_rest) + self.r_m * I_net) / self.tau_m

        # 4. Integración iterativa
        self.v += dv * self.dt

        # 5. Chequear umbral para disparar (Spike)
        if self.v >= self.v_thresh:
            self.has_spiked = True

            # Registrar estadísticas de spike
            isi = self.t_current - self.t_last_spike
            if self.t_last_spike > -500:  # Evitar contar el primer spike
                self.isi_history.append(isi)

            self.t_last_spike = self.t_current
            self.spike_count += 1

            # Actualizar tasa de disparo
            if len(self.isi_history) > 0:
                avg_isi = sum(self.isi_history) / len(self.isi_history)
                self.firing_rate = 1000.0 / avg_isi if avg_isi > 0 else 0.0

            # Sobrescribir historial con pico visual
            self.membrane_history[-1] = self.v_thresh * 1.5

            # Aplicar adaptación: incrementar I_adap por spike
            self.I_adap += self.delta_adap

            # Reseteo del sistema
            self.v = self.v_reset
            self.t_rest = self.t_ref

        self._save_history()
        return self.has_spiked

    def get_stats(self):
        """Retorna un diccionario con estadísticas actuales de la neurona."""
        refractory_pct = max(0, (self.t_rest / self.t_ref) * 100)
        return {
            'voltage': self.v,
            'firing_rate': self.firing_rate,
            'spike_count': self.spike_count,
            'refractory_pct': refractory_pct,
            'adaptation': self.I_adap,
            'isi_avg': sum(self.isi_history) / len(self.isi_history) if self.isi_history else 0.0
        }

    def _save_history(self):
        self.membrane_history.append(self.v)
