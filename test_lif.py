#!/usr/bin/env python
"""
Test script para neurona_lif.py — verifica lógica sin pygame
"""
from neurona_lif import LIFNeuron

def test_basic_lif():
    """Test de comportamiento básico LIF."""
    print("=" * 60)
    print("TEST 1: Comportamiento Básico LIF")
    print("=" * 60)

    neuron = LIFNeuron()
    print(f"Estado inicial: V={neuron.v:.3f}, Spikes={neuron.spike_count}")

    # Inyectar corriente por 50 pasos para generar spikes
    for i in range(50):
        spiked = neuron.update(I_excit=5.0)
        if i % 10 == 0 or spiked:
            stats = neuron.get_stats()
            print(f"  Step {i:3d}: V={neuron.v:+.3f}, Spike={spiked}, "
                  f"Rate={stats['firing_rate']:.1f}Hz, Adapt={stats['adaptation']:.3f}")

    print(f"\nTotal spikes: {neuron.spike_count}\n")


def test_sfa():
    """Test de Spike Frequency Adaptation (SFA)."""
    print("=" * 60)
    print("TEST 2: Spike Frequency Adaptation")
    print("=" * 60)

    neuron = LIFNeuron()
    print("Inyectando corriente constante: I_excit = 4.0\n")

    spike_times = []
    for i in range(200):
        spiked = neuron.update(I_excit=4.0)
        if spiked:
            spike_times.append(i)
            stats = neuron.get_stats()
            print(f"  Spike #{neuron.spike_count} en step {i}: "
                  f"Rate={stats['firing_rate']:.1f}Hz, Adapt={stats['adaptation']:.3f}")

    print(f"\nTotal spikes: {neuron.spike_count}")
    if len(spike_times) > 1:
        isis = [spike_times[i + 1] - spike_times[i] for i in range(len(spike_times) - 1)]
        print(f"ISIs: {isis}")
        print(f"ISI promedio: {sum(isis) / len(isis):.1f} ms")
    print()


def test_inhibition():
    """Test de corriente inhibitoria."""
    print("=" * 60)
    print("TEST 3: Inhibición vs Excitación")
    print("=" * 60)

    neuron_excit = LIFNeuron(name="Excitatory")
    neuron_inhib = LIFNeuron(name="Inhibitory")

    print("Paso 1: Solo excitatorio (I_excit=6.0)\n")
    for i in range(30):
        neuron_excit.update(I_excit=6.0)
        if i % 10 == 0:
            print(f"  Step {i:2d}: V_excit={neuron_excit.v:+.3f}")

    print(f"Spikes (excit only): {neuron_excit.spike_count}\n")

    print("Paso 2: Excitatorio + Inhibitorio (I_excit=6.0, I_inhib=4.0)\n")
    for i in range(30):
        neuron_inhib.update(I_excit=6.0, I_inhib=4.0)
        if i % 10 == 0:
            print(f"  Step {i:2d}: V_inhib={neuron_inhib.v:+.3f}")

    print(f"Spikes (with inhibition): {neuron_inhib.spike_count}\n")


def test_reset():
    """Test de reset function."""
    print("=" * 60)
    print("TEST 4: Reset Function")
    print("=" * 60)

    neuron = LIFNeuron()

    # Generar actividad
    for i in range(50):
        neuron.update(I_excit=5.0)

    stats_before = neuron.get_stats()
    print(f"Antes del reset:")
    print(f"  Voltage: {stats_before['voltage']:.3f}")
    print(f"  Spike count: {stats_before['spike_count']}")
    print(f"  Firing rate: {stats_before['firing_rate']:.1f} Hz")
    print(f"  Adaptation: {stats_before['adaptation']:.3f}\n")

    # Reset
    neuron.reset()
    stats_after = neuron.get_stats()

    print(f"Después del reset:")
    print(f"  Voltage: {stats_after['voltage']:.3f}")
    print(f"  Spike count: {stats_after['spike_count']}")
    print(f"  Firing rate: {stats_after['firing_rate']:.1f} Hz")
    print(f"  Adaptation: {stats_after['adaptation']:.3f}\n")


def test_refractory():
    """Test de período refractario."""
    print("=" * 60)
    print("TEST 5: Refractory Period")
    print("=" * 60)

    neuron = LIFNeuron()
    print(f"t_ref = {neuron.t_ref} ms\n")

    # Inyección fuerte para forzar spike
    for i in range(50):
        spiked = neuron.update(I_excit=10.0)
        if i < 15 or spiked or neuron.t_rest > 0:
            stats = neuron.get_stats()
            print(f"  Step {i:2d}: V={neuron.v:+.4f}, "
                  f"Ref={stats['refractory_pct']:5.1f}%, Spike={spiked}")

    print()


if __name__ == "__main__":
    test_basic_lif()
    test_sfa()
    test_inhibition()
    test_reset()
    test_refractory()

    print("=" * 60)
    print("✓ Todos los tests completados sin errores")
    print("=" * 60)
