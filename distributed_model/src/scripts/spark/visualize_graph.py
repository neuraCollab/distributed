import os
import time
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rcParams
from tqdm import tqdm
import cugraph
import cudf

# Настройки
rcParams['figure.figsize'] = (20, 12)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class EnhancedGPUGraphVisualizer:
    def __init__(self, graphml_path):
        self.graphml_path = graphml_path
        self.cpu_graph = None
        self.gpu_graph = None
        self.pos = None

    def load_graph_with_positions(self):
        """Загрузка графа с предварительно вычисленными позициями"""
        print("🔄 Загрузка графа и позиций...")
        
        # Чтение графа и позиций из GraphML
        self.cpu_graph = nx.read_graphml(self.graphml_path)
        
        # Извлечение позиций из атрибутов узлов
        if all('x' in data and 'y' in data for _, data in self.cpu_graph.nodes(data=True)):
            self.pos = {n: (data['x'], data['y']) for n, data in self.cpu_graph.nodes(data=True)}
            print("✅ Позиции загружены из атрибутов графа")
        else:
            print("⚠️ Позиции не найдены в графе. Будет выполнен расчет на GPU")

    def convert_to_gpu(self):
        """Конвертация графа в cuGraph формат"""
        edges = [(u, v) for u, v in self.cpu_graph.edges()]
        gdf = cudf.DataFrame(edges, columns=['src', 'dst'])
        self.gpu_graph = cugraph.Graph(directed=True)
        self.gpu_graph.from_cudf_edgelist(gdf, source='src', destination='dst')

    def compute_gpu_layout(self):
        """Дополнительная оптимизация позиций на GPU"""
        if self.pos is None:
            print("\n🧮 Вычисление Force Atlas 2 на GPU...")
            start = time.time()
            
            gpu_pos = cugraph.force_atlas2(
                self.gpu_graph,
                max_iter=100,
                pos_list=None,
                barnes_hut_optimize=True
            )
            
            self.pos = {k: (v[0], v[1]) for k, v in zip(gpu_pos['vertex'], 
                                                      zip(gpu_pos['x'], gpu_pos['y']))}
            print(f"✅ GPU-оптимизация позиций завершена за {time.time()-start:.2f} сек")

    def visualize(self, output_png="graph.png", highlight_top=20):
        """Визуализация с matplotlib"""
        print("\n🎨 Визуализация...")
        start = time.time()
        
        # Создаем фигуру с предустановленными размерами из rcParams
        fig, ax = plt.subplots(figsize=rcParams['figure.figsize'])
        
        # Вычисление центральности
        degree_centrality = nx.degree_centrality(self.cpu_graph)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:highlight_top]
        
        # Рисуем все узлы
        nx.draw_networkx_nodes(
            self.cpu_graph,
            pos=self.pos,
            node_size=1,
            node_color='blue',
            alpha=0.3,
            ax=ax
        )
        
        # Выделяем топ-узлы
        nx.draw_networkx_nodes(
            self.cpu_graph,
            pos=self.pos,
            nodelist=[n for n, _ in top_nodes],
            node_size=50,
            node_color='red',
            alpha=0.8,
            ax=ax
        )
        
        # Подписи для топ-узлов
        labels = {n: n for n, _ in top_nodes}
        nx.draw_networkx_labels(
            self.cpu_graph,
            pos=self.pos,
            labels=labels,
            font_size=8,
            font_color='black',
            ax=ax
        )
        
        # Рёбра
        nx.draw_networkx_edges(
            self.cpu_graph,
            pos=self.pos,
            edge_color='gray',
            alpha=0.05,
            width=0.1,
            ax=ax
        )
        
        ax.set_title("Optimized Chess Network (OpenOrd + GPU Enhanced)", fontsize=24)
        ax.axis('off')
        plt.savefig(output_png, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Визуализация сохранена в {output_png} за {time.time()-start:.2f} сек")

    def create_interactive(self, output_html="interactive.html"):
        """Интерактивная визуализация с PyVis"""
        try:
            from pyvis.network import Network
            
            print("\n💻 Создание интерактивной визуализации...")
            
            sample_nodes = list(self.cpu_graph.nodes())[:5000]
            subgraph = self.cpu_graph.subgraph(sample_nodes)
            
            net = Network(
                height="900px",
                width="100%",
                notebook=False,
                directed=True,
                bgcolor="#222222",
                font_color="white"
            )
            
            for node in tqdm(subgraph.nodes(), desc="Добавление узлов"):
                x, y = self.pos.get(node, (0, 0))
                net.add_node(
                    node,
                    x=x*1000,
                    y=y*1000,
                    size=5,
                    color="#3a7bd5"
                )
            
            for edge in tqdm(subgraph.edges(), desc="Добавление рёбер"):
                net.add_edge(edge[0], edge[1], width=0.1, color="#cccccc")
            
            net.set_options("""
            {
              "physics": {
                "stabilization": {
                  "enabled": true,
                  "iterations": 100
                },
                "repulsion": {
                  "nodeDistance": 100
                }
              }
            }
            """)
            
            net.save_graph(output_html)
            print(f"✅ Интерактивная версия сохранена в {output_html}")
            
        except ImportError:
            print("⚠️ PyVis не установлен. Для интерактивности: pip install pyvis")

if __name__ == "__main__":
    visualizer = EnhancedGPUGraphVisualizer("graph_time.graphml")
    visualizer.load_graph_with_positions()
    visualizer.convert_to_gpu()
    visualizer.compute_gpu_layout()
    visualizer.visualize("chess_network.png", highlight_top=50)
    visualizer.create_interactive("chess_interactive.html")