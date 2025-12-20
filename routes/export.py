"""
Routes pour l'export des associations en CSV et PDF.
"""
import csv
import io
from datetime import datetime
from flask import Blueprint, make_response, jsonify
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from storage.database import db, Association
from utils.auth import token_required

# Créer le Blueprint pour les routes d'export
export_bp = Blueprint('export', __name__)


@export_bp.route('/export/csv', methods=['GET'])
@token_required
def export_csv():
    """
    Exporte toutes les associations non archivées en format CSV.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        CSV: Fichier CSV avec les colonnes: participant, gift, created_at
    """
    # Récupérer toutes les associations non archivées
    associations = Association.query.filter_by(is_archived=False).order_by(Association.created_at).all()
    
    # Créer un buffer en mémoire pour le CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Écrire l'en-tête
    writer.writerow(['Personne1', 'Personne2', 'Date de création'])
    
    # Écrire les données
    for assoc in associations:
        writer.writerow([
            assoc.personne1,
            assoc.personne2,
            assoc.created_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.created_at else ''
        ])
    
    # Créer la réponse
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=associations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


@export_bp.route('/export/pdf', methods=['GET'])
@token_required
def export_pdf():
    """
    Exporte toutes les associations non archivées en format PDF.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        PDF: Fichier PDF formaté avec tableau des associations
    """
    # Récupérer toutes les associations non archivées
    associations = Association.query.filter_by(is_archived=False).order_by(Association.created_at).all()
    
    # Créer un buffer en mémoire pour le PDF
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Titre
    title = Paragraph("Rapport des Associations", title_style)
    elements.append(title)
    
    # Date de génération
    date_text = Paragraph(
        f"<para align=center>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</para>",
        styles['Normal']
    )
    elements.append(date_text)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Statistiques
    total_text = Paragraph(
        f"<para align=center><b>Total des associations: {len(associations)}</b></para>",
        styles['Normal']
    )
    elements.append(total_text)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Données du tableau
    data = [['Personne1', 'Personne2', 'Date de création']]
    
    for assoc in associations:
        data.append([
            str(assoc.personne1),
            str(assoc.personne2),
            assoc.created_at.strftime('%d/%m/%Y %H:%M:%S') if assoc.created_at else 'N/A'
        ])
    
    # Créer le tableau
    table = Table(data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
    
    # Style du tableau
    table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corps du tableau
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Grille
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternance de couleurs pour les lignes
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 0.5 * inch))
    footer_text = Paragraph(
        "<para align=center><i>Document généré automatiquement par l'application d'association</i></para>",
        styles['Italic']
    )
    elements.append(footer_text)
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le contenu du buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Créer la réponse
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=associations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response
