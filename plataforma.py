import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from psycopg2 import Error
import bcrypt
from tkinter import font
import hashlib

# ==================== Conexão ====================
DB_CONFIG = {
    'dbname': 'eduplatform',
    'user': 'postgres',
    'password': '27112002',
    'host': 'localhost',
    'port': '1520'
}

TIPOS_ACESSO = {
    'aluno': ['minhas_info', 'minhas_notas'],
    'professor': ['gerenciar_alunos', 'cadastrar_notas', 'ver_todos_alunos'],
    'admin': ['gerenciar_usuarios', 'cadastrar_professor', 'excluir_usuario', 'ver_todos_usuarios']
}

class Database:
    
    @staticmethod
    def get_connection():
        try:
            return psycopg2.connect(**DB_CONFIG)
        except Error as e:
            messagebox.showerror("Erro", f"Erro de conexão: {e}")
            return None

# ==================== TELA DE LOGIN ====================
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 Plataforma Educacional - Login")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.setup_ui()
        
    def setup_ui(self):
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Título
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(self.root, text="🎓 EDUPLATFORM", font=title_font, 
                              bg="#2c3e50", fg="white", pady=20)
        title_label.pack(fill=tk.X)
        
        # Frame login
        login_frame = tk.Frame(self.root, bg="#ecf0f1", pady=30)
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Email
        tk.Label(login_frame, text="📧 Email:", font=("Arial", 12), bg="#ecf0f1").pack(pady=10)
        self.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        self.email_entry.pack(pady=5)
        self.email_entry.focus()
        
        # Senha
        tk.Label(login_frame, text="🔒 Senha:", font=("Arial", 12), bg="#ecf0f1").pack(pady=10)
        self.senha_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, show="*")
        self.senha_entry.pack(pady=5)
        
        # Botão login
        login_btn = tk.Button(login_frame, text="ENTRAR", font=("Arial", 14, "bold"),
                             bg="#3498db", fg="white", width=15, height=2,
                             command=self.login, cursor="hand2")
        login_btn.pack(pady=30)
        
        # Enter para login
        self.root.bind('<Return>', lambda e: self.login())
        
    def login(self):
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get()
        
        if not email or not senha:
            messagebox.showwarning("Aviso", "Preencha email e senha!")
            return
        
        conn = Database.get_connection()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, senha, tipo FROM usuarios WHERE email = %s", (email,))
            usuario = cur.fetchone()
            
            if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario[2].encode('utf-8')):
                tipo = usuario[3]
                nome = usuario[1]
                cur.close()
                conn.close()
                
                self.root.destroy()
                MainWindow(usuario_id=usuario[0], nome=nome, tipo=tipo)
            else:
                messagebox.showerror("Erro", "Email ou senha incorretos!")
                
        except Error as e:
            messagebox.showerror("Erro", f"Erro no login: {e}")
        finally:
            if conn:
                conn.close()
    
    def run(self):
        self.root.mainloop()

# ==================== TELA PRINCIPAL ====================
class MainWindow:
    def __init__(self, usuario_id, nome, tipo):
        self.usuario_id = usuario_id
        self.nome = nome
        self.tipo = tipo
        self.root = tk.Tk()
        self.root.title(f"🎓 EduPlatform - {nome} ({tipo.title()})")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.setup_ui()
        
    def setup_ui(self):
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Top frame com info do usuário
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        top_frame.pack(fill=tk.X, pady=0)
        top_frame.pack_propagate(False)
        
        user_label = tk.Label(top_frame, text=f"👋 Bem-vindo, {self.nome}!", 
                             font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        user_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        tipo_label = tk.Label(top_frame, text=f"Perfi: {self.tipo.title()}", 
                             font=("Arial", 12), bg="#2c3e50", fg="#3498db")
        tipo_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        logout_btn = tk.Button(top_frame, text="🚪 Sair", font=("Arial", 10),
                              bg="#e74c3c", fg="white", command=self.root.quit)
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=20)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Criar abas baseadas no tipo de usuário
        self.criar_abas()
        
    def criar_abas(self):
        if self.tipo == 'aluno':
            self.criar_aba_aluno()
        elif self.tipo == 'professor':
            self.criar_aba_professor()
        elif self.tipo == 'admin':
            self.criar_aba_admin()
    
    def criar_aba_aluno(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📚 Minhas Informações")
        
        # Info pessoal
        info_frame = tk.LabelFrame(frame, text="Informações Pessoais", font=("Arial", 12, "bold"))
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(info_frame, text="Nome:", font=("Arial", 11)).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        tk.Label(info_frame, text=self.nome, font=("Arial", 11, "bold")).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Notas (simulado)
        notas_frame = tk.LabelFrame(frame, text="📊 Minhas Notas", font=("Arial", 12, "bold"))
        notas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(notas_frame, columns=('Disciplina', 'Nota', 'Status'), show='headings')
        tree.heading('Disciplina', text='Disciplina')
        tree.heading('Nota', text='Nota')
        tree.heading('Status', text='Status')
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dados simulados
        for disciplina, nota in [('Matemática', 8.5), ('Português', 7.0), ('História', 9.2)]:
            status = "APROVADO" if nota >= 7 else "RECUPERAÇÃO"
            tree.insert('', 'end', values=(disciplina, f"{nota}/10", status))
    
    def criar_aba_professor(self):
        # Aba geral
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👨‍🏫 Gerenciar Alunos")
        
        # Treeview para listar alunos
        tree_frame = tk.LabelFrame(frame, text="Lista de Alunos", font=("Arial", 12, "bold"))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.alunos_tree = ttk.Treeview(tree_frame, columns=('ID', 'Nome', 'Email', 'Tipo'), show='headings')
        self.alunos_tree.heading('ID', text='ID')
        self.alunos_tree.heading('Nome', text='Nome')
        self.alunos_tree.heading('Email', text='Email')
        self.alunos_tree.heading('Tipo', text='Tipo')
        self.alunos_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botões
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="🔢 Cadastrar Nota", bg="#f39c12", fg="white",
                 command=lambda: messagebox.showinfo("Nota", "Funcionalidade em desenvolvimento")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📝 Ver Detalhes", bg="#3498db", fg="white",
                 command=self.ver_detalhes_aluno).pack(side=tk.LEFT, padx=5)
    
    def criar_aba_admin(self):
        # Aba usuários
        usuarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(usuarios_frame, text="👥 Gerenciar Usuários")
        
        # Treeview usuários
        tree_frame = tk.LabelFrame(usuarios_frame, text="Todos os Usuários", font=("Arial", 12, "bold"))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.usuarios_tree = ttk.Treeview(tree_frame, columns=('ID', 'Nome', 'Email', 'Tipo'), show='headings')
        self.usuarios_tree.heading('ID', text='ID')
        self.usuarios_tree.heading('Nome', text='Nome')
        self.usuarios_tree.heading('Email', text='Email')
        self.usuarios_tree.heading('Tipo', text='Tipo')
        self.usuarios_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botões admin
        btn_frame = tk.Frame(usuarios_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="➕ Novo Usuário", bg="#27ae60", fg="white",
                 command=self.novo_usuario).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Excluir", bg="#e74c3c", fg="white",
                 command=self.excluir_usuario).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Atualizar", bg="#9b59b6", fg="white",
                 command=self.atualizar_usuarios).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_usuarios()
    
    def ver_detalhes_aluno(self):
        selected = self.alunos_tree.selection()
        if selected:
            item = self.alunos_tree.item(selected)
            messagebox.showinfo("Detalhes", f"Aluno: {item['values'][1]}\nEmail: {item['values'][2]}")
        else:
            messagebox.showwarning("Aviso", "Selecione um aluno!")
    
    def novo_usuario(self):
        nome = simpledialog.askstring("Novo Usuário", "Nome:")
        email = simpledialog.askstring("Novo Usuário", "Email:")
        senha = simpledialog.askstring("Novo Usuário", "Senha:", show="*")
        tipo = simpledialog.askstring("Novo Usuário", "Tipo (aluno/professor):", initialvalue="aluno")
        
        if nome and email and senha:
            conn = Database.get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s,%s,%s,%s) RETURNING id",
                               (nome, email, senha_hash, tipo))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Usuário cadastrado!")
                    self.atualizar_usuarios()
                except Error as e:
                    messagebox.showerror("Erro", str(e))
                finally:
                    conn.close()
    
    def excluir_usuario(self):
        selected = self.usuarios_tree.selection()
        if selected:
            usuario_id = self.usuarios_tree.item(selected)['values'][0]
            if messagebox.askyesno("Confirmar", "Excluir este usuário?"):
                conn = Database.get_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                        conn.commit()
                        messagebox.showinfo("Sucesso", "Usuário excluído!")
                        self.atualizar_usuarios()
                    except Error:
                        messagebox.showerror("Erro", "Erro ao excluir!")
                    finally:
                        conn.close()
    
    def atualizar_usuarios(self):
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
            
        conn = Database.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, nome, email, tipo FROM usuarios ORDER BY nome")
                for row in cur.fetchall():
                    self.usuarios_tree.insert('', 'end', values=row)
            finally:
                conn.close()
    
    def run(self):
        self.root.mainloop()

# ==================== INICIAR APLICAÇÃO ====================
if __name__ == "__main__":
    # Criar usuário admin se não existir
    conn = Database.get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM usuarios WHERE email = 'admin@eduplatform.com'")
            if not cur.fetchone():
                senha_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s,%s,%s,%s)",
                           ("Administrador", "admin@eduplatform.com", senha_hash, "admin"))
                conn.commit()
                print("✅ Usuário admin criado: admin@eduplatform.com / admin123")
        except Error as e:
            print(f"Erro ao criar admin: {e}")
        finally:
            conn.close()
    
    # Iniciar login
    app = LoginWindow()
    app.run()