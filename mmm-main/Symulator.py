import math

class Symulator:

    def __init__(self):
        self._wykres_wejscia = None
        self._wykres_wyjscia = None
        self._parametry = None


    def send_information(self, wykres_wejscia, wykres_wyjscia, parametry):
        if (wykres_wejscia is None) or (wykres_wyjscia is None) or (parametry is None):
            raise ValueError('Podano nieprawidłowe parametry symulacji.')

        self._wykres_wejscia = wykres_wejscia
        self._wykres_wyjscia = wykres_wyjscia
        self._parametry = parametry   

 
    def run_simulation(self):

    # Deklaracja sygnałów: prostokątnego, sinusoidalnego, trójkątnego
        def impulse(time_on, time_off, time, force, offset, amplitude):                                 # prostokątny
            if (time_on > time or time_off < time):
                force = offset
            else:
                force = offset + amplitude
            return force

        def sine(time, force, offset, amplitude, period, phase):                                        # harmoniczny
            force = offset + amplitude * math.sin(time/period * 2*math.pi + phase*2*math.pi/360)
            return force

        def triangle(time, force, offset, amplitude, period, phase):                                    # trójkątny
            while ((time + phase) >= period):
                time = time - period 
            if((time + phase) <= (period/4)):
                force = amplitude*4*(time + phase)/period
            elif((time + phase) <= (2/4*period)):
                force = amplitude - amplitude*4*(time + phase-period/4)/period
            elif((time + phase) <= (3/4*period)):
                force = - amplitude*4*(time + phase-2*period/4)/period
            elif((time + phase) <= (period)):
                force = - amplitude + amplitude*4*(time + phase -3/4*period)/period
            return (force + offset)

    # Zczytywanie parametrów od użytkownika + deklaracje zmiennych: time i force oraz tablic tab_... do wyświetlania wyników na wykresach
        if self._parametry["signal_type"] == "impulse":
            time_on =           self._parametry["signal_parameters"]["Czas włączenia"]
            time_off =          self._parametry["signal_parameters"]["Czas wyłączenia"]
            offset =            self._parametry["signal_parameters"]["Offset"]
        elif self._parametry["signal_type"] == "sine":
            period =            self._parametry["signal_parameters"]["Okres"]
            phase =             self._parametry["signal_parameters"]["Faza początkowa"]
            offset =            self._parametry["signal_parameters"]["Składowa stała"]
        else:   # triangle
            period =            self._parametry["signal_parameters"]["Okres"]
            phase =             self._parametry["signal_parameters"]["Opóźnienie"]
            offset =            self._parametry["signal_parameters"]["Offset"]
        
        amplitude =             self._parametry["signal_parameters"]["Amplituda"]
        m =                     self._parametry["model_parameters"]["Masa (m)"]
        k =                     self._parametry["model_parameters"]["Stała sprężyny (k)"]
        b =                     self._parametry["model_parameters"]["Tłumienie (b)"]  
        x0 =                    self._parametry["simulation_parameters"]["Położenie początkowe (x0)"]
        v0 =                    self._parametry["simulation_parameters"]["Prędkość początkowa (v0)"]
        step =                  self._parametry["simulation_parameters"]["Krok symulacji (h)"]
        simulation_time =       self._parametry["simulation_parameters"]["Czas symulacji (ts)"]
        time =                  0
        force =                 0

        # Dodatkowa walidacja danych (HB):
        if m == 0:  # W modelu stanowym występuje dzielenie przez zero
            raise ValueError("Niepoprawne dane: model nie funkcjonuje dla zerowej masy.")
        if self._parametry["signal_type"] == "impulse" and time_on > time_off:
            raise ValueError('Niepoprawne dane: czas wyłączenia impulsu jest mniejszy, niż czas włączenia.')
        if simulation_time < 0:
            raise ValueError('Niepoprawne dane: ujemny czas symulacji')

        
        # zapisuje dane do naniesienia na wykresy
        tab_x_now_eu = []
        tab_v_now_eu = []
        tab_x_now_rk = []
        tab_v_now_rk = []

    # Automatyczna regulacja wysokości - wyszukiwanie najdalszego od osi x punktu 
        i   = 0     # ilość punktów do naniesienia
        max = 0     # zapisuje odległość najadlszego od osi x punktu 
        while (simulation_time >= time):
            # wybór sygnału wejściowego - siły (force)
            if self._parametry["signal_type"] == "impulse":
                force = impulse(time_on, time_off, time, force, offset, amplitude)
            elif self._parametry["signal_type"] == "sine":
                force = sine(time, force, offset, amplitude, period, phase)
            else:   #triangle
                force = triangle(time, force, offset, amplitude, period, phase)
                 
            # pierwsza próbka Euler i RK-4
            if time == 0:
                x_now_eu = x0
                v_now_eu = v0
                x_now_rk = x0
                v_now_rk = v0
            else:
                # kolejne próbki Euler
                x_now_eu = x_before_eu + step * v_before_eu
                v_now_eu = v_before_eu + step * ((1/m)*force - (k/m)*x_before_eu - (b/m)*v_before_eu)

                # koljene próbki RK-4 
                a1 = v_before_rk
                b1 = v_before_rk + step/2 * a1
                c1 = v_before_rk + step/2 * b1
                d1 = v_before_rk + step   * c1
                x_now_rk = x_before_rk + step/6 * (a1+2*b1+2*c1+d1)
                
                a2 = (1/m)*force - (k/m)*x_before_rk - (b/m)*v_before_rk
                b2 = (1/m)*force - (k/m)*(x_before_rk + step/2*a2) - (b/m)*(v_before_rk + step/2*a2)
                c2 = (1/m)*force - (k/m)*(x_before_rk + step/2*b2) - (b/m)*(v_before_rk + step/2*b2)
                d2 = (1/m)*force - (k/m)*(x_before_rk + step  *c2) - (b/m)*(v_before_rk + step  *c2)
                v_now_rk = v_before_rk + step/6 * (a2+2*b2+2*c2+d2)

            # przygotowania do koljnego kroku
            time = time + step
            x_before_eu = x_now_eu
            v_before_eu = v_now_eu
            x_before_rk = x_now_rk
            v_before_rk = v_now_rk

            # przypisywanie wartości punktów do tablic z których rysujemy funkcje
            tab_x_now_eu.append(x_now_eu)
            tab_v_now_eu.append(v_now_eu)
            tab_x_now_rk.append(x_now_rk)
            tab_v_now_rk.append(v_now_rk)
            i = i + 1
            
            # szukanie największej liczby - potrzebne do autoregulacji osi y 
            if  (abs(x_now_eu) > max):
                max = abs(x_now_eu)
            elif((abs(v_now_eu) > max)):
                max = abs(v_now_eu)
            elif((abs(x_now_rk) > max)):
                max = abs(x_now_rk)
            elif((abs(v_now_rk) > max)):
                max = abs(v_now_rk)
        
        time = 0
        
    # Ustawienie parametrów wykresu wyjścia
        self._wykres_wyjscia.configure(xscale=simulation_time/10, yscale=max/7, xdiv_number=11, ydiv_number=8, xdesc='t', ydesc='y')
        self._wykres_wyjscia.create_new_plot_area()
        if (self._parametry["euler"] == True and self._parametry["runge_kutta"] == True):
            self._wykres_wyjscia.legend.add_entries(('położenie_euler','prędkość_euler','położenie_rk4','prędkość_rk4'))
        elif self._parametry["euler"] == True:
            self._wykres_wyjscia.legend.add_entries(('położenie_euler','prędkość_euler'))
        elif self._parametry["runge_kutta"] == True:
            self._wykres_wyjscia.legend.add_entries(('położenie_rk4','prędkość_rk4'))

    # Ustawienie parametrów wykresu wejścia
        self._wykres_wejscia.configure(xscale=simulation_time/10, yscale=(amplitude+abs(offset))/5, xdiv_number=11, ydiv_number=6, xdesc='t', ydesc='y')
        self._wykres_wejscia.create_new_plot_area()
        if self._parametry["signal_type"] == "impulse":
            self._wykres_wejscia.legend.add_entries(('prostokątny', ))
        elif self._parametry["signal_type"] == "sine":
            self._wykres_wejscia.legend.add_entries(('sinus', ))
        else:   # triangle
            self._wykres_wejscia.legend.add_entries(('trójkątny', ))   

     
    # Nanoszenie punktów na wykresy
        k = 0
        while (i > k):

            # nanoszenie próbek na wykres wejścia
            if self._parametry["signal_type"] == "impulse":
                force = impulse(time_on, time_off, time, force, offset, amplitude)
            elif self._parametry["signal_type"] == "sine":
                force = sine(time, force, offset, amplitude, period, phase)
            else:   #triangle
                force = triangle(time, force, offset, amplitude, period, phase)
            self._wykres_wejscia.active_plot = 0 
            self._wykres_wejscia.add_data_point((time, force))


            # nanoszenie próbek na wykres wyjścia
            if (self._parametry["euler"] == True and self._parametry["runge_kutta"] == True):
                self._wykres_wyjscia.active_plot = 0
                self._wykres_wyjscia.add_data_point((time, tab_x_now_eu[k]))
                self._wykres_wyjscia.active_plot = 1
                self._wykres_wyjscia.add_data_point((time, tab_v_now_eu[k]))
                self._wykres_wyjscia.active_plot = 2
                self._wykres_wyjscia.add_data_point((time, tab_x_now_rk[k]))
                self._wykres_wyjscia.active_plot = 3
                self._wykres_wyjscia.add_data_point((time, tab_v_now_rk[k]))
            elif self._parametry["euler"] == True:
                self._wykres_wyjscia.active_plot = 0
                self._wykres_wyjscia.add_data_point((time, tab_x_now_eu[k]))
                self._wykres_wyjscia.active_plot = 1
                self._wykres_wyjscia.add_data_point((time, tab_v_now_eu[k]))
            elif self._parametry["runge_kutta"] == True:
                self._wykres_wyjscia.active_plot = 0
                self._wykres_wyjscia.add_data_point((time, tab_x_now_rk[k]))
                self._wykres_wyjscia.active_plot = 1
                self._wykres_wyjscia.add_data_point((time, tab_v_now_rk[k]))

            time = time + step
            k = k + 1
