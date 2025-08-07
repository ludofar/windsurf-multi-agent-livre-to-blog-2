"""
Tests d'intégration pour le système de conversion de livre en blog.
"""
import os
import asyncio
import pytest
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Désactiver les logs pendant les tests
logger.remove()

# Chemin vers le dossier de test
TEST_DIR = Path(__file__).parent
SAMPLE_TXT = TEST_DIR / "samples" / "sample.txt"
OUTPUT_DIR = TEST_DIR / "output"

@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asynchrones."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def sample_txt():
    """Retourne le chemin vers le fichier texte de test."""
    if not SAMPLE_TXT.exists():
        pytest.skip(f"Fichier de test introuvable : {SAMPLE_TXT}")
    return SAMPLE_TXT

@pytest.fixture(scope="session")
def output_dir():
    """Crée et retourne le dossier de sortie pour les tests."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR

@pytest.mark.asyncio
async def test_text_analysis(sample_txt, output_dir):
    """Teste l'analyse d'un fichier texte."""
    from agents.pdf_analyzer import PDFAnalyzerAgent
    
    # Initialiser l'agent
    analyzer = PDFAnalyzerAgent("test_analyzer")
    
    # Lire le contenu du fichier
    with open(sample_txt, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analyser le contenu
    result = await analyzer.analyze_text(content)
    
    # Vérifier les résultats
    assert result is not None
    assert "metadata" in result
    assert "content" in result
    assert len(result["content"]) > 0
    
    logger.info(f"Analyse de texte réussie : {len(result['content'])} sections trouvées")
    return True

@pytest.mark.asyncio
async def test_blog_generation(sample_txt, output_dir):
    """Teste la génération d'un article de blog à partir d'un texte."""
    from agents.pdf_analyzer import PDFAnalyzerAgent
    from agents.blog_writer import BlogWriterAgent
    
    # Lire le contenu du fichier
    with open(sample_txt, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analyser le contenu
    analyzer = PDFAnalyzerAgent("test_analyzer")
    analysis = await analyzer.analyze_text(content)
    
    # Générer l'article de blog
    writer = BlogWriterAgent("test_writer")
    blog_post = await writer.generate_blog_post(analysis)
    
    # Vérifier les résultats
    assert blog_post is not None
    assert "title" in blog_post
    assert "content" in blog_post
    assert len(blog_post["content"]) > 0
    
    # Sauvegarder le résultat
    output_file = output_dir / "test_blog_post.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {blog_post['title']}\n\n")
        f.write(blog_post["content"])
    
    logger.info(f"Article de blog généré : {output_file}")
    return True

@pytest.mark.asyncio
async def test_end_to_end_workflow(sample_txt, output_dir):
    """Teste le workflow complet de conversion texte vers blog."""
    from workflow.daily_workflow import DailyWorkflow
    
    # Créer une instance du workflow
    workflow = DailyWorkflow(
        input_dir=sample_txt.parent,
        output_dir=output_dir,
        file_pattern="*.txt"
    )
    
    # Exécuter le workflow
    results = await workflow.run()
    
    # Vérifier les résultats
    assert results is not None
    assert len(results) > 0
    
    for result in results:
        assert "input_file" in result
        assert "output_file" in result
        assert "success" in result
        assert result["success"] is True
        assert Path(result["output_file"]).exists()
    
    logger.info(f"Workflow terminé avec succès : {len(results)} fichiers traités")
    return True

if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([
        "-v",
        "--log-cli-level=INFO",
        "--cov=agents",
        "--cov=workflow",
        "--cov-report=term-missing"
    ])
