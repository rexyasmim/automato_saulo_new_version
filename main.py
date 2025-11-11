import ttkbootstrap as tb  
from model.banco import DatabaseManager
from model.model import AutomatonModel
from view.view import AutomatonView
from controller.controller import AutomatonController

def main():
    
    # 1. Cria a janela raiz (agora com um tema!)
    #    Temas escuros bons: "superhero", "darkly", "cyborg", "vapor" (roxo)
    #    Temas claros bons: "litera", "cosmo", "flatly"
    root = tb.Window(themename="vapor") 
    
    try:
        db_manager = DatabaseManager(db_file="automata.db")
        db_manager.connect() 
        model = AutomatonModel(db_manager)
    except Exception as e:
        print(f"Erro fatal ao inicializar o Model: {e}")
        root.destroy()
        return

    view = AutomatonView(root)
    
    controller = AutomatonController(model, view)
    
    # 5. Inicia a Aplicação
    def on_closing():
        print("Fechando a aplicação...")
        db_manager.close() 
        root.destroy()     

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop() 

if __name__ == "__main__":
    main()