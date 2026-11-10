"""
Módulo GUI en Tkinter para Práctica 3: Autómatas Finitos No Deterministas con Transiciones Lambda (AFN-λ).
ESCOM - IPN - Teoría de la Computación
Autores: Mario García Castillo & Antonio Navarro Domínguez
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, List, Set

import sys
# Asegurar que 'src' esté en sys.path si se ejecuta desde la raíz o desde src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automata import Automata
from formatos import FormatosAutomata
from algoritmos_afn import (
    calcular_clausura_lambda,
    calcular_todas_clausuras_lambda,
    simulacion_directa_paso_a_paso,
    eliminar_transiciones_lambda_detallado,
    construccion_subconjuntos_detallada,
)
from minimizacion import (
    minimizar_afd_detallado,
    son_equivalentes,
    verificar_equivalencia_isomorfica,
)
from validador_lotes import (
    procesar_lote_cadenas,
    guardar_informe_lote,
)


class VentanaPractica3(tk.Tk):
    """Ventana Principal de la Práctica 3 con Tkinter y ttk."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Práctica 3: Autómatas Finitos No Deterministas con Transiciones Lambda (AFN-λ) - ESCOM IPN")
        self.geometry("1150x750")
        self.minsize(950, 650)

        # Estado global de la aplicación
        self.automata_actual: Optional[Automata] = None
        self.ruta_archivo_actual: Optional[str] = None
        
        # Estado para simulación paso a paso (Tab 2)
        self.simulacion_pasos: List[Dict[str, Any]] = []
        self.simulacion_indice: int = 0
        self.simulacion_cadena_actual: str = ""

        # Configurar estilos ttk
        self._configurar_estilos()

        # Construir interfaz principal con pestañas (Notebook)
        self._construir_interfaz()

    def _configurar_estilos(self) -> None:
        """Configura una paleta de colores moderna y limpia con ttk."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", font=("Segoe UI", 10))
        style.configure("TNotebook", background="#f0f2f5", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 8])
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"), foreground="#1a365d")
        style.configure("SubHeading.TLabel", font=("Segoe UI", 10, "bold"), foreground="#2b6cb0")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), background="#3182ce", foreground="white")
        style.map("Accent.TButton", background=[("active", "#2b6cb0"), ("pressed", "#2c5282")])

    def _construir_interfaz(self) -> None:
        """Construye el contenedor principal con pestañas y barra de estado."""
        # Barra superior con archivo actual
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.lbl_archivo = ttk.Label(
            top_frame,
            text="Ningún autómata cargado (.jff). Por favor cargue un archivo en la pestaña 1.",
            font=("Segoe UI", 10, "italic"),
            foreground="#718096"
        )
        self.lbl_archivo.pack(side=tk.LEFT, padx=5)

        btn_cargar_rapido = ttk.Button(top_frame, text="📁 Cargar .jff Rápido", command=self._cargar_jff_global)
        btn_cargar_rapido.pack(side=tk.RIGHT, padx=5)

        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear pestañas
        self.tab_importar = ttk.Frame(self.notebook, padding=10)
        self.tab_simulacion = ttk.Frame(self.notebook, padding=10)
        self.tab_eliminar_lambda = ttk.Frame(self.notebook, padding=10)
        self.tab_subconjuntos = ttk.Frame(self.notebook, padding=10)
        self.tab_minimizacion = ttk.Frame(self.notebook, padding=10)
        self.tab_lotes = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_importar, text="1. Importar & Cerradura λ")
        self.notebook.add(self.tab_simulacion, text="2. Simulación Paso a Paso")
        self.notebook.add(self.tab_eliminar_lambda, text="3. Eliminar Transiciones λ")
        self.notebook.add(self.tab_subconjuntos, text="4. Subconjuntos (AFN→AFD)")
        self.notebook.add(self.tab_minimizacion, text="5. Minimización & Equivalencia")
        self.notebook.add(self.tab_lotes, text="6. Validación Masiva Lotes")

        # Inicializar contenido de cada pestaña
        self._init_tab_importar()
        self._init_tab_simulacion()
        self._init_tab_eliminar_lambda()
        self._init_tab_subconjuntos()
        self._init_tab_minimizacion()
        self._init_tab_lotes()

        # Barra de estado inferior
        status_frame = ttk.Frame(self, padding=5)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_status = ttk.Label(
            status_frame,
            text="Estado: Listo. Desarrollado para Teoría de la Computación (ESCOM IPN).",
            font=("Segoe UI", 9),
            foreground="#4a5568"
        )
        self.lbl_status.pack(side=tk.LEFT, padx=5)

    def _actualizar_info_archivo(self, ruta: str) -> None:
        """Actualiza la referencia al archivo actual y refresca pestañas."""
        self.ruta_archivo_actual = ruta
        nombre = os.path.basename(ruta)
        self.lbl_archivo.config(
            text=f"Autómata activo: {nombre} ({ruta})",
            font=("Segoe UI", 10, "bold"),
            foreground="#2b6cb0"
        )
        self.lbl_status.config(text=f"Autómata cargado exitosamente desde {nombre}")

    def _cargar_jff_global(self) -> None:
        """Selector global de archivos .jff."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo JFLAP (.jff)",
            filetypes=[("Archivos JFLAP", "*.jff"), ("Todos los archivos", "*.*")]
        )
        if not archivo:
            return
        try:
            auto = FormatosAutomata.cargar_jff(archivo)
            self.automata_actual = auto
            self._actualizar_info_archivo(archivo)
            self._poblar_datos_importar()
            messagebox.showinfo("Éxito", f"Autómata cargado correctamente:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo JFLAP:\n{str(e)}")

    # =========================================================================
    # TAB 1: Importar .jff y Cerradura λ
    # =========================================================================
    def _init_tab_importar(self) -> None:
        frame = self.tab_importar

        # Panel superior: Botón de carga y resumen de quíntupla
        top_bar = ttk.Frame(frame)
        top_bar.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_cargar = ttk.Button(top_bar, text="📂 Cargar Archivo .jff", style="Accent.TButton", command=self._tab1_cargar)
        btn_cargar.pack(side=tk.LEFT, padx=5)

        lbl_title = ttk.Label(top_bar, text="Quíntupla del Autómata (G = (Q, Σ, δ, q0, F))", style="Heading.TLabel")
        lbl_title.pack(side=tk.LEFT, padx=15)

        # Contenedor dividido: Izquierda (Quíntupla text), Derecha (Cerraduras λ)
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Izquierda: Quíntupla
        frame_q = ttk.LabelFrame(paned, text=" Información de la Quíntupla ", padding=10)
        paned.add(frame_q, weight=1)

        self.txt_quintupla = tk.Text(frame_q, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748")
        scroll_q = ttk.Scrollbar(frame_q, orient=tk.VERTICAL, command=self.txt_quintupla.yview)
        self.txt_quintupla.configure(yscrollcommand=scroll_q.set)
        self.txt_quintupla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_q.pack(side=tk.RIGHT, fill=tk.Y)

        # Derecha: Cerraduras Lambda
        frame_lambda = ttk.LabelFrame(paned, text=" Cálculo de Cerraduras Lambda (λ-clausura) ", padding=10)
        paned.add(frame_lambda, weight=1)

        ctrl_lambda = ttk.Frame(frame_lambda)
        ctrl_lambda.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Label(ctrl_lambda, text="Estado:").pack(side=tk.LEFT, padx=5)
        self.combo_estados_lambda = ttk.Combobox(ctrl_lambda, state="readonly", width=15)
        self.combo_estados_lambda.pack(side=tk.LEFT, padx=5)

        btn_clausura_unitaria = ttk.Button(ctrl_lambda, text="Calcular λ-clausura", command=self._tab1_calcular_unitaria)
        btn_clausura_unitaria.pack(side=tk.LEFT, padx=5)

        btn_todas_clausuras = ttk.Button(ctrl_lambda, text="Calcular Todas", command=self._tab1_calcular_todas)
        btn_todas_clausuras.pack(side=tk.LEFT, padx=5)

        self.txt_lambda_res = tk.Text(frame_lambda, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748")
        scroll_l = ttk.Scrollbar(frame_lambda, orient=tk.VERTICAL, command=self.txt_lambda_res.yview)
        self.txt_lambda_res.configure(yscrollcommand=scroll_l.set)
        self.txt_lambda_res.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        scroll_l.pack(side=tk.RIGHT, fill=tk.Y)

    def _tab1_cargar(self) -> None:
        self._cargar_jff_global()

    def _poblar_datos_importar(self) -> None:
        if not self.automata_actual:
            return
        auto = self.automata_actual

        # Formatear quíntupla
        texto = f"Q (Estados): {sorted(list(auto.estados))}\n"
        texto += f"Σ (Alfabeto): {sorted(list(auto.alfabeto))}\n"
        texto += f"q0 (Inicial): {auto.inicial}\n"
        texto += f"F (Finales): {sorted(list(auto.finales))}\n"
        texto += f"δ (Transiciones totales): {len(auto.transiciones)}\n\n"
        texto += "--- Detalle de Transiciones ---\n"
        for origen, simbolo, destino in sorted(list(auto.transiciones)):
            sim_str = "λ" if simbolo == "" else simbolo
            texto += f"  δ({origen}, {sim_str}) -> {destino}\n"

        self.txt_quintupla.delete("1.0", tk.END)
        self.txt_quintupla.insert(tk.END, texto)

        # Llenar combobox de estados
        estados_ordenados = sorted(list(auto.estados))
        self.combo_estados_lambda['values'] = estados_ordenados
        if estados_ordenados:
            self.combo_estados_lambda.set(estados_ordenados[0])

        # Limpiar resultados lambda
        self.txt_lambda_res.delete("1.0", tk.END)
        self.txt_lambda_res.insert(tk.END, "Seleccione un estado o presione 'Calcular Todas' para ver las λ-clausuras.")

    def _tab1_calcular_unitaria(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        estado = self.combo_estados_lambda.get()
        if not estado:
            messagebox.showwarning("Advertencia", "Seleccione un estado válido.")
            return
        try:
            clausura = calcular_clausura_lambda(self.automata_actual, estado)
            res = f"λ-clausura({estado}) = {sorted(list(clausura))}\n"
            self.txt_lambda_res.delete("1.0", tk.END)
            self.txt_lambda_res.insert(tk.END, res)
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular λ-clausura: {str(e)}")

    def _tab1_calcular_todas(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        try:
            todas = calcular_todas_clausuras_lambda(self.automata_actual)
            res = "=== Lambda-Clausuras de todos los estados ===\n\n"
            for q, claus in todas.items():
                res += f"  λ-clausura({q}) = {sorted(list(claus))}\n"
            self.txt_lambda_res.delete("1.0", tk.END)
            self.txt_lambda_res.insert(tk.END, res)
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular todas las λ-clausuras: {str(e)}")

    # =========================================================================
    # TAB 2: Simulación Directa Paso a Paso (AFN-λ)
    # =========================================================================
    def _init_tab_simulacion(self) -> None:
        frame = self.tab_simulacion

        # Panel de entrada de cadena y botones de control
        top_frame = ttk.LabelFrame(frame, text=" Control de Simulación Directa (AFN-λ) ", padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        form_frame = ttk.Frame(top_frame)
        form_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Label(form_frame, text="Cadena a simular (dejar vacío para λ):").pack(side=tk.LEFT, padx=5)
        self.entry_cadena = ttk.Entry(form_frame, width=30, font=("Consolas", 11))
        self.entry_cadena.pack(side=tk.LEFT, padx=5)

        btn_simular = ttk.Button(form_frame, text="▶ Iniciar Simulación", style="Accent.TButton", command=self._tab2_iniciar_simulacion)
        btn_simular.pack(side=tk.LEFT, padx=10)

        # Botones paso a paso
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.btn_paso_anterior = ttk.Button(nav_frame, text="◀ Paso Anterior", command=self._tab2_paso_anterior, state=tk.DISABLED)
        self.btn_paso_anterior.pack(side=tk.LEFT, padx=5)

        self.btn_paso_siguiente = ttk.Button(nav_frame, text="Paso Siguiente ▶", command=self._tab2_paso_siguiente, state=tk.DISABLED)
        self.btn_paso_siguiente.pack(side=tk.LEFT, padx=5)

        self.btn_ejecutar_todo = ttk.Button(nav_frame, text="⏭ Ejecutar Todo", command=self._tab2_ejecutar_todo, state=tk.DISABLED)
        self.btn_ejecutar_todo.pack(side=tk.LEFT, padx=5)

        self.btn_reiniciar = ttk.Button(nav_frame, text="🔄 Reiniciar", command=self._tab2_reiniciar, state=tk.DISABLED)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)

        self.lbl_paso_estado = ttk.Label(nav_frame, text="Paso: 0 / 0", font=("Segoe UI", 10, "bold"), foreground="#2b6cb0")
        self.lbl_paso_estado.pack(side=tk.RIGHT, padx=10)

        # Panel de visualización detallada del paso actual
        res_frame = ttk.LabelFrame(frame, text=" Detalle del Paso Actual ", padding=10)
        res_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        self.txt_sim_detalle = tk.Text(res_frame, wrap=tk.WORD, font=("Consolas", 11), bg="#f7fafc", fg="#2d3748")
        scroll_s = ttk.Scrollbar(res_frame, orient=tk.VERTICAL, command=self.txt_sim_detalle.yview)
        self.txt_sim_detalle.configure(yscrollcommand=scroll_s.set)
        self.txt_sim_detalle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_s.pack(side=tk.RIGHT, fill=tk.Y)

    def _tab2_iniciar_simulacion(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        cadena = self.entry_cadena.get().strip()
        self.simulacion_cadena_actual = cadena
        try:
            # simulacion_directa_paso_a_paso retorna (aceptada, lista_pasos)
            aceptada, pasos = simulacion_directa_paso_a_paso(self.automata_actual, cadena)
            self.simulacion_pasos = pasos
            self.simulacion_indice = 0

            if not pasos:
                messagebox.showinfo("Información", "La simulación no generó pasos.")
                return

            self.btn_paso_anterior.config(state=tk.NORMAL)
            self.btn_paso_siguiente.config(state=tk.NORMAL)
            self.btn_ejecutar_todo.config(state=tk.NORMAL)
            self.btn_reiniciar.config(state=tk.NORMAL)

            self._tab2_mostrar_paso_actual()
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar simulación: {str(e)}")

    def _tab2_mostrar_paso_actual(self) -> None:
        if not self.simulacion_pasos:
            return
        idx = self.simulacion_indice
        total = len(self.simulacion_pasos)
        paso = self.simulacion_pasos[idx]

        self.lbl_paso_estado.config(text=f"Paso: {idx + 1} / {total}")

        txt = f"========================================\n"
        txt += f"  PASO {idx + 1} DE {total}\n"
        txt += f"========================================\n\n"
        txt += f"Cadena evaluada: '{self.simulacion_cadena_actual}'\n"
        txt += f"Símbolo leído: '{paso.get('simbolo', 'λ / Inicial')}'\n\n"
        
        estados_antes = paso.get('estados_antes_clausura', paso.get('estados_antes', set()))
        estados_despues = paso.get('estados_despues_clausura', paso.get('estados_despues', set()))
        transiciones = paso.get('transiciones_tomadas', [])

        txt += f"• Estados antes de λ-clausura: {sorted(list(estados_antes))}\n"
        txt += f"• Transiciones tomadas con símbolo: {transiciones}\n"
        txt += f"• Estados después de λ-clausura: {sorted(list(estados_despues))}\n\n"

        if idx == total - 1:
            aceptada = paso.get('aceptada', False)
            txt += f"----------------------------------------\n"
            if aceptada:
                txt += f"RESULTADO FINAL: ¡CADENA ACEPTADA! ✅\n"
                txt += f"El conjunto final contiene estados de aceptación ({sorted(list(self.automata_actual.finales))}).\n"
            else:
                txt += f"RESULTADO FINAL: CADENA RECHAZADA ❌\n"
                txt += f"El conjunto final no contiene ningún estado de aceptación.\n"
            txt += f"----------------------------------------\n"

        self.txt_sim_detalle.delete("1.0", tk.END)
        self.txt_sim_detalle.insert(tk.END, txt)

        # Controlar estado de botones
        self.btn_paso_anterior.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        self.btn_paso_siguiente.config(state=tk.NORMAL if idx < total - 1 else tk.DISABLED)

    def _tab2_paso_siguiente(self) -> None:
        if self.simulacion_indice < len(self.simulacion_pasos) - 1:
            self.simulacion_indice += 1
            self._tab2_mostrar_paso_actual()

    def _tab2_paso_anterior(self) -> None:
        if self.simulacion_indice > 0:
            self.simulacion_indice -= 1
            self._tab2_mostrar_paso_actual()

    def _tab2_ejecutar_todo(self) -> None:
        if not self.simulacion_pasos:
            return
        self.simulacion_indice = len(self.simulacion_pasos) - 1
        self._tab2_mostrar_paso_actual()

    def _tab2_reiniciar(self) -> None:
        if not self.simulacion_pasos:
            return
        self.simulacion_indice = 0
        self._tab2_mostrar_paso_actual()

    # =========================================================================
    # TAB 3: Eliminación de Transiciones λ Paso a Paso
    # =========================================================================
    def _init_tab_eliminar_lambda(self) -> None:
        frame = self.tab_eliminar_lambda

        top_frame = ttk.Frame(frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_ejecutar = ttk.Button(top_frame, text="⚡ Eliminar Transiciones λ Detallado", style="Accent.TButton", command=self._tab3_ejecutar)
        btn_ejecutar.pack(side=tk.LEFT, padx=5)

        btn_exportar = ttk.Button(top_frame, text="💾 Exportar AFN Resultante (.jff)", command=self._tab3_exportar)
        btn_exportar.pack(side=tk.LEFT, padx=5)

        # PanedWindow para bitácora y tabla de transiciones añadidas
        paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Arriba: Resumen de cambios y estados de aceptación
        frame_res = ttk.LabelFrame(paned, text=" Cambios en Estados de Aceptación y Justificación ", padding=10)
        paned.add(frame_res, weight=1)

        self.txt_elim_res = tk.Text(frame_res, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748", height=8)
        scroll_e1 = ttk.Scrollbar(frame_res, orient=tk.VERTICAL, command=self.txt_elim_res.yview)
        self.txt_elim_res.configure(yscrollcommand=scroll_e1.set)
        self.txt_elim_res.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_e1.pack(side=tk.RIGHT, fill=tk.Y)

        # Abajo: Tabla de transiciones añadidas
        frame_tabla = ttk.LabelFrame(paned, text=" Nuevas Transiciones Añadidas (δ' q, a -> p) ", padding=10)
        paned.add(frame_tabla, weight=2)

        columns = ("origen", "simbolo", "destino", "justificacion")
        self.tree_trans_nuevas = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=10)
        self.tree_trans_nuevas.heading("origen", text="Origen")
        self.tree_trans_nuevas.heading("simbolo", text="Símbolo")
        self.tree_trans_nuevas.heading("destino", text="Destino")
        self.tree_trans_nuevas.heading("justificacion", text="Justificación / Ruta λ")

        self.tree_trans_nuevas.column("origen", width=100, anchor=tk.CENTER)
        self.tree_trans_nuevas.column("simbolo", width=80, anchor=tk.CENTER)
        self.tree_trans_nuevas.column("destino", width=100, anchor=tk.CENTER)
        self.tree_trans_nuevas.column("justificacion", width=450, anchor=tk.W)

        scroll_tree = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_trans_nuevas.yview)
        self.tree_trans_nuevas.configure(yscrollcommand=scroll_tree.set)
        self.tree_trans_nuevas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree.pack(side=tk.RIGHT, fill=tk.Y)

        self.afn_sin_lambda_cache: Optional[Automata] = None

    def _tab3_ejecutar(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        try:
            afn_nuevo, bitacora = eliminar_transiciones_lambda_detallado(self.automata_actual)
            self.afn_sin_lambda_cache = afn_nuevo

            # Mostrar resumen de aceptación
            txt = "=== ELIMINACIÓN DE TRANSICIONES LAMBDA ===\n\n"
            txt += f"• Estados iniciales: {afn_nuevo.inicial}\n"
            txt += f"• Nuevos estados finales: {sorted(list(afn_nuevo.finales))}\n\n"
            txt += "Justificación de estados de aceptación (F' = { q | λ-cl(q) ∩ F ≠ ∅ }):\n"
            just_aceptacion = bitacora.get("justificacion_finales", {})
            for q, raz in just_aceptacion.items():
                txt += f"  - Estado {q}: es de aceptación porque su λ-clausura {raz} contiene estados finales.\n"

            self.txt_elim_res.delete("1.0", tk.END)
            self.txt_elim_res.insert(tk.END, txt)

            # Llenar treeview con transiciones añadidas
            for row in self.tree_trans_nuevas.get_children():
                self.tree_trans_nuevas.delete(row)

            trans_nuevas = bitacora.get("transiciones_nuevas", [])
            for t in trans_nuevas:
                origen = t.get("origen", "")
                sim = t.get("simbolo", "")
                dest = t.get("destino", "")
                just = t.get("justificacion", "")
                self.tree_trans_nuevas.insert("", tk.END, values=(origen, sim, dest, just))

            messagebox.showinfo("Éxito", "Transiciones λ eliminadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar transiciones λ: {str(e)}")

    def _tab3_exportar(self) -> None:
        if not self.afn_sin_lambda_cache:
            messagebox.showwarning("Advertencia", "Primero ejecute la eliminación de transiciones λ en la pestaña 3.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".jff",
            filetypes=[("Archivos JFLAP", "*.jff"), ("Todos los archivos", "*.*")],
            title="Guardar AFN sin transiciones lambda"
        )
        if not archivo:
            return
        try:
            FormatosAutomata.guardar_jff(self.afn_sin_lambda_cache, archivo)
            messagebox.showinfo("Éxito", f"AFN guardado exitosamente en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

    # =========================================================================
    # TAB 4: Construcción de Subconjuntos Paso a Paso (AFN -> AFD)
    # =========================================================================
    def _init_tab_subconjuntos(self) -> None:
        frame = self.tab_subconjuntos

        top_frame = ttk.Frame(frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_ejecutar = ttk.Button(top_frame, text="⚙️ Ejecutar Construcción de Subconjuntos", style="Accent.TButton", command=self._tab4_ejecutar)
        btn_ejecutar.pack(side=tk.LEFT, padx=5)

        btn_exportar = ttk.Button(top_frame, text="💾 Exportar AFD Resultante (.jff)", command=self._tab4_exportar)
        btn_exportar.pack(side=tk.LEFT, padx=5)

        # Tabla de transiciones del AFD conforme se descubren subconjuntos
        frame_tabla = ttk.LabelFrame(frame, text=" Tabla de Transiciones del AFD Generado (Construcción por Subconjuntos) ", padding=10)
        frame_tabla.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Columnas dinámicas según alfabeto, pero fijaremos un Treeview flexible
        self.tree_afd = ttk.Treeview(frame_tabla, show="headings", height=12)
        self.tree_afd.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_afd = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_afd.yview)
        self.tree_afd.configure(yscrollcommand=scroll_afd.set)
        scroll_afd.pack(side=tk.RIGHT, fill=tk.Y)

        self.afd_resultado_cache: Optional[Automata] = None

    def _tab4_ejecutar(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        try:
            afd, bitacora = construccion_subconjuntos_detallada(self.automata_actual)
            self.afd_resultado_cache = afd

            filas = bitacora.get("filas", [])
            alfabeto = sorted(list(afd.alfabeto))

            # Configurar columnas del treeview
            cols = ["estado_afd", "subconjunto_afn", "es_inicial", "es_aceptacion"] + alfabeto
            self.tree_afd["columns"] = cols

            self.tree_afd.heading("estado_afd", text="Estado AFD")
            self.tree_afd.heading("subconjunto_afn", text="Subconjunto AFN equivalente")
            self.tree_afd.heading("es_inicial", text="Inicial?")
            self.tree_afd.heading("es_aceptacion", text="Aceptación? (Justificación)")
            for sym in alfabeto:
                self.tree_afd.heading(sym, text=f"δ(s, {sym})")

            self.tree_afd.column("estado_afd", width=90, anchor=tk.CENTER)
            self.tree_afd.column("subconjunto_afn", width=180, anchor=tk.W)
            self.tree_afd.column("es_inicial", width=70, anchor=tk.CENTER)
            self.tree_afd.column("es_aceptacion", width=250, anchor=tk.W)
            for sym in alfabeto:
                self.tree_afd.column(sym, width=120, anchor=tk.CENTER)

            # Limpiar filas anteriores
            for row in self.tree_afd.get_children():
                self.tree_afd.delete(row)

            for f in filas:
                est = f.get("estado_afd", "")
                sub = str(sorted(list(f.get("subconjunto", []))))
                ini = "Sí" if f.get("es_inicial", False) else ""
                
                # Aceptación y justificación
                es_ac = f.get("es_aceptacion", False)
                intersec = f.get("interseccion_finales", set())
                if es_ac:
                    ac_str = f"Sí (contiene finales: {sorted(list(intersec))})"
                else:
                    ac_str = "No (sin intersección con F)"

                trans = f.get("transiciones", {})
                valores = [est, sub, ini, ac_str]
                for sym in alfabeto:
                    dest_sub = trans.get(sym, set())
                    valores.append(str(sorted(list(dest_sub))) if dest_sub else "∅")

                self.tree_afd.insert("", tk.END, values=tuple(valores))

            messagebox.showinfo("Éxito", f"AFD construido correctamente con {len(afd.estados)} estados.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la construcción de subconjuntos: {str(e)}")

    def _tab4_exportar(self) -> None:
        if not self.afd_resultado_cache:
            messagebox.showwarning("Advertencia", "Primero ejecute la construcción de subconjuntos en la pestaña 4.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".jff",
            filetypes=[("Archivos JFLAP", "*.jff"), ("Todos los archivos", "*.*")],
            title="Guardar AFD resultante"
        )
        if not archivo:
            return
        try:
            FormatosAutomata.guardar_jff(self.afd_resultado_cache, archivo)
            messagebox.showinfo("Éxito", f"AFD guardado exitosamente en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

    # =========================================================================
    # TAB 5: Minimización de AFD y Comparación de Equivalencia
    # =========================================================================
    def _init_tab_minimizacion(self) -> None:
        frame = self.tab_minimizacion

        paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sección 1: Minimización
        frame_min = ttk.LabelFrame(paned, text=" Minimización de AFD Paso a Paso (Myhill-Nerode / Hopcroft) ", padding=10)
        paned.add(frame_min, weight=1)

        top_min = ttk.Frame(frame_min)
        top_min.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_minimizar = ttk.Button(top_min, text="📉 Minimizar AFD Actual", style="Accent.TButton", command=self._tab5_minimizar)
        btn_minimizar.pack(side=tk.LEFT, padx=5)

        self.txt_min_res = tk.Text(frame_min, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748", height=10)
        scroll_m = ttk.Scrollbar(frame_min, orient=tk.VERTICAL, command=self.txt_min_res.yview)
        self.txt_min_res.configure(yscrollcommand=scroll_m.set)
        self.txt_min_res.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        scroll_m.pack(side=tk.RIGHT, fill=tk.Y)

        # Sección 2: Comparación de Equivalencia entre dos Autómatas
        frame_eq = ttk.LabelFrame(paned, text=" Comparación de Equivalencia entre Dos Autómatas (.jff)", padding=10)
        paned.add(frame_eq, weight=1)

        eq_form = ttk.Frame(frame_eq)
        eq_form.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Label(eq_form, text="Segundo Autómata (.jff):").pack(side=tk.LEFT, padx=5)
        self.entry_segundo_jff = ttk.Entry(eq_form, width=45, font=("Consolas", 10))
        self.entry_segundo_jff.pack(side=tk.LEFT, padx=5)

        btn_sel_segundo = ttk.Button(eq_form, text="📁 Examinar...", command=self._tab5_seleccionar_segundo)
        btn_sel_segundo.pack(side=tk.LEFT, padx=5)

        btn_comparar = ttk.Button(eq_form, text="⚖️ Verificar Equivalencia", style="Accent.TButton", command=self._tab5_comparar)
        btn_comparar.pack(side=tk.LEFT, padx=10)

        self.txt_eq_res = tk.Text(frame_eq, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748", height=6)
        scroll_eq = ttk.Scrollbar(frame_eq, orient=tk.VERTICAL, command=self.txt_eq_res.yview)
        self.txt_eq_res.configure(yscrollcommand=scroll_eq.set)
        self.txt_eq_res.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        scroll_eq.pack(side=tk.RIGHT, fill=tk.Y)

        self.ruta_segundo_jff: Optional[str] = None

    def _tab5_minimizar(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata en la pestaña 1.")
            return
        try:
            # Asegurarnos de que sea AFD (o convertirlo / minimizarlo directamente)
            # minimizar_afd_detallado requiere AFD o realiza subconjuntos si es necesario
            afd_min, bitacora = minimizar_afd_detallado(self.automata_actual)

            txt = "=== MINIMIZACIÓN DE AFD ===\n\n"
            inacc = bitacora.get("estados_inaccesibles", set())
            txt += f"• Estados inaccesibles eliminados: {sorted(list(inacc))}\n\n"
            txt += "• Particiones por rondas (P0, P1, P2...):\n"
            rondas = bitacora.get("rondas", [])
            for idx, r in enumerate(rondas):
                txt += f"  - Ronda P{idx}: {r}\n"

            part_final = bitacora.get("particion_final", [])
            txt += f"\n• Partición final de clases de equivalencia: {part_final}\n"
            txt += f"• Estados en el AFD mínimo resultante: {len(afd_min.estados)}\n"

            self.txt_min_res.delete("1.0", tk.END)
            self.txt_min_res.insert(tk.END, txt)
            messagebox.showinfo("Éxito", "Minimización de AFD completada.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al minimizar AFD: {str(e)}")

    def _tab5_seleccionar_segundo(self) -> None:
        archivo = filedialog.askopenfilename(
            title="Seleccionar segundo autómata JFLAP (.jff)",
            filetypes=[("Archivos JFLAP", "*.jff"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_segundo_jff = archivo
            self.entry_segundo_jff.delete(0, tk.END)
            self.entry_segundo_jff.insert(0, archivo)

    def _tab5_comparar(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata principal en la pestaña 1.")
            return
        if not self.ruta_segundo_jff:
            messagebox.showwarning("Advertencia", "Seleccione un segundo archivo .jff para comparar.")
            return
        try:
            auto2 = FormatosAutomata.cargar_jff(self.ruta_segundo_jff)
            equivalentes = son_equivalentes(self.automata_actual, auto2)
            isomorficos, msg = verificar_equivalencia_isomorfica(self.automata_actual, auto2)

            txt = "=== RESULTADO DE COMPARACIÓN DE EQUIVALENCIA ===\n\n"
            if equivalentes:
                txt += "✅ LOS AUTÓMATAS SON EQUIVALENTES (Reconocen exactamente el mismo lenguaje).\n"
            else:
                txt += "❌ LOS AUTÓMATAS NO SON EQUIVALENTES (Reconocen lenguajes distintos).\n"

            if isomorficos:
                txt += "✅ Son isomorfos (sus autómatas mínimos coinciden salvo renombre de estados).\n"
            else:
                txt += f"ℹ️ Detalle estructural: {msg}\n"

            self.txt_eq_res.delete("1.0", tk.END)
            self.txt_eq_res.insert(tk.END, txt)
        except Exception as e:
            messagebox.showerror("Error", f"Error al comparar autómatas: {str(e)}")

    # =========================================================================
    # TAB 6: Validación Masiva por Lotes
    # =========================================================================
    def _init_tab_lotes(self) -> None:
        frame = self.tab_lotes

        top_frame = ttk.Frame(frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_cargar_lote = ttk.Button(top_frame, text="📂 Cargar Archivo .txt de Cadenas", style="Accent.TButton", command=self._tab6_cargar_lote)
        btn_cargar_lote.pack(side=tk.LEFT, padx=5)

        self.lbl_lote_info = ttk.Label(top_frame, text="Ningún archivo de lotes cargado.", font=("Segoe UI", 10))
        self.lbl_lote_info.pack(side=tk.LEFT, padx=15)

        btn_guardar_informe = ttk.Button(top_frame, text="💾 Guardar Informe (.txt)", command=self._tab6_guardar_informe)
        btn_guardar_informe.pack(side=tk.RIGHT, padx=5)

        # PanedWindow para tabla de resultados y resumen estadístico
        paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Arriba: Tabla de resultados
        frame_tabla = ttk.LabelFrame(paned, text=" Resultados de Validación por Lotes ", padding=10)
        paned.add(frame_tabla, weight=3)

        columns = ("linea", "cadena", "longitud", "resultado", "pasos")
        self.tree_lotes = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=12)
        self.tree_lotes.heading("linea", text="Línea")
        self.tree_lotes.heading("cadena", text="Cadena")
        self.tree_lotes.heading("longitud", text="Longitud")
        self.tree_lotes.heading("resultado", text="Resultado")
        self.tree_lotes.heading("pasos", text="Pasos / Trazas")

        self.tree_lotes.column("linea", width=60, anchor=tk.CENTER)
        self.tree_lotes.column("cadena", width=250, anchor=tk.W)
        self.tree_lotes.column("longitud", width=80, anchor=tk.CENTER)
        self.tree_lotes.column("resultado", width=120, anchor=tk.CENTER)
        self.tree_lotes.column("pasos", width=400, anchor=tk.W)

        scroll_lote = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_lotes.yview)
        self.tree_lotes.configure(yscrollcommand=scroll_lote.set)
        self.tree_lotes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_lote.pack(side=tk.RIGHT, fill=tk.Y)

        # Abajo: Resumen estadístico
        frame_stat = ttk.LabelFrame(paned, text=" Resumen Estadístico del Lote ", padding=10)
        paned.add(frame_stat, weight=1)

        self.txt_lote_stat = tk.Text(frame_stat, wrap=tk.WORD, font=("Consolas", 10), bg="#f7fafc", fg="#2d3748", height=5)
        self.txt_lote_stat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.resultados_lote_cache: Optional[Dict[str, Any]] = None

    def _tab6_cargar_lote(self) -> None:
        if not self.automata_actual:
            messagebox.showwarning("Advertencia", "Primero cargue un autómata principal en la pestaña 1.")
            return
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de texto con cadenas (.txt)",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not archivo:
            return
        try:
            resultados = procesar_lote_cadenas(self.automata_actual, archivo)
            self.resultados_lote_cache = resultados

            self.lbl_lote_info.config(text=f"Archivo procesado: {os.path.basename(archivo)}")

            # Limpiar tabla
            for row in self.tree_lotes.get_children():
                self.tree_lotes.delete(row)

            items = resultados.get("resultados", [])
            for item in items:
                lin = item.get("linea", 0)
                cad = item.get("cadena", "")
                lon = item.get("longitud", len(cad))
                res = "ACEPTADA ✅" if item.get("aceptada", False) else "RECHAZADA ❌"
                pas = str(item.get("pasos", ""))
                self.tree_lotes.insert("", tk.END, values=(lin, cad, lon, res, pas))

            # Resumen estadístico
            total = resultados.get("total", 0)
            aceptadas = resultados.get("aceptadas", 0)
            rechazadas = resultados.get("rechazadas", 0)
            porcentaje = resultados.get("porcentaje_exito", 0.0)

            txt_stat = f"• Total de cadenas procesadas: {total}\n"
            txt_stat += f"• Cadenas aceptadas: {aceptadas}\n"
            txt_stat += f"• Cadenas rechazadas: {rechazadas}\n"
            txt_stat += f"• Porcentaje de aceptación: {porcentaje:.2f}%\n"

            self.txt_lote_stat.delete("1.0", tk.END)
            self.txt_lote_stat.insert(tk.END, txt_stat)

            messagebox.showinfo("Éxito", f"Lote procesado exitosamente: {total} cadenas evaluadas.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar lote de cadenas: {str(e)}")

    def _tab6_guardar_informe(self) -> None:
        if not self.resultados_lote_cache:
            messagebox.showwarning("Advertencia", "Primero procese un archivo de lotes en la pestaña 6.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar informe de lote"
        )
        if not archivo:
            return
        try:
            guardar_informe_lote(self.resultados_lote_cache, archivo)
            messagebox.showinfo("Éxito", f"Informe guardado exitosamente en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el informe: {str(e)}")


if __name__ == "__main__":
    app = VentanaPractica3()
    app.mainloop()
