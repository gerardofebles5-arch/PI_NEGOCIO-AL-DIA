"""
Módulo de generación de dashboard para (π)NAD
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class DashboardGenerator:
    """Generador de dashboard para (π)NAD"""
    
    def __init__(self):
        """Inicializar generador de dashboard"""
        self.client_data = {}  # {client_id: client_dashboard_data}
    
    def create_client_dashboard(self, client_id: str, transactions: List[Dict], 
                               period: str = 'current_month') -> Dict:
        """
        Crear dashboard para cliente
        
        Args:
            client_id: ID del cliente
            transactions: Lista de transacciones del cliente
            period: Período (current_month, last_month, custom)
            
        Returns:
            Diccionario con datos del dashboard
        """
        # Filtrar transacciones por período
        filtered_transactions = self._filter_by_period(transactions, period)
        
        # Calcular métricas
        summary = self._calculate_summary(filtered_transactions)
        
        # Generar datos de gráficos
        charts = self._generate_charts(filtered_transactions)
        
        # Calcular distribución por categoría
        category_distribution = self._calculate_category_distribution(filtered_transactions)
        
        # Comparar con período anterior
        comparison = self._compare_with_previous(transactions, period)
        
        dashboard_data = {
            'client_id': client_id,
            'period': period,
            'generated_date': datetime.now().isoformat(),
            'summary': summary,
            'charts': charts,
            'category_distribution': category_distribution,
            'comparison': comparison,
            'transactions': filtered_transactions
        }
        
        self.client_data[client_id] = dashboard_data
        
        return dashboard_data
    
    def _filter_by_period(self, transactions: List[Dict], period: str) -> List[Dict]:
        """Filtrar transacciones por período"""
        if period == 'current_month':
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return [
                t for t in transactions
                if datetime.fromisoformat(t['date']) >= start_of_month
            ]
        elif period == 'last_month':
            now = datetime.now()
            start_of_last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_of_last_month = now.replace(day=1) - timedelta(days=1)
            return [
                t for t in transactions
                if start_of_last_month <= datetime.fromisoformat(t['date']) <= end_of_last_month
            ]
        else:
            return transactions
    
    def _calculate_summary(self, transactions: List[Dict]) -> Dict:
        """Calcular resumen ejecutivo"""
        total_revenue = sum(
            t['amount'] for t in transactions 
            if t['type'] == 'sale' and t['status'] == 'validated'
        )
        
        total_expenses = sum(
            t['amount'] for t in transactions 
            if t['type'] in ['purchase', 'expense'] and t['status'] == 'validated'
        )
        
        net_income = total_revenue - total_expenses
        
        tax_collected = sum(
            t.get('tax_amount', 0) for t in transactions 
            if t['type'] == 'sale' and t['status'] == 'validated'
        )
        
        tax_paid = sum(
            t.get('tax_amount', 0) for t in transactions 
            if t['type'] in ['purchase', 'expense'] and t['status'] == 'validated'
        )
        
        margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0.0
        
        return {
            'revenue': {
                'total': total_revenue,
                'transaction_count': sum(1 for t in transactions if t['type'] == 'sale'),
                'average_transaction': total_revenue / sum(1 for t in transactions if t['type'] == 'sale') if sum(1 for t in transactions if t['type'] == 'sale') > 0 else 0
            },
            'expenses': {
                'total': total_expenses,
                'transaction_count': sum(1 for t in transactions if t['type'] in ['purchase', 'expense']),
                'average_transaction': total_expenses / sum(1 for t in transactions if t['type'] in ['purchase', 'expense']) if sum(1 for t in transactions if t['type'] in ['purchase', 'expense']) > 0 else 0
            },
            'net_income': {
                'total': net_income,
                'margin': margin
            },
            'tax': {
                'collected': tax_collected,
                'paid': tax_paid,
                'net': tax_collected - tax_paid
            },
            'total_transactions': len(transactions),
            'validated_transactions': sum(1 for t in transactions if t['status'] == 'validated'),
            'pending_transactions': sum(1 for t in transactions if t['status'] == 'pending')
        }
    
    def _generate_charts(self, transactions: List[Dict]) -> Dict:
        """Generar datos para gráficos"""
        # Gráfico de evolución temporal (ingresos y egresos por día)
        revenue_trend = self._generate_revenue_trend(transactions)
        
        # Gráfico de distribución de gastos
        expense_distribution = self._generate_expense_distribution(transactions)
        
        # Gráfico de ingresos por categoría
        revenue_by_category = self._generate_revenue_by_category(transactions)
        
        return {
            'revenue_trend': revenue_trend,
            'expense_distribution': expense_distribution,
            'revenue_by_category': revenue_by_category
        }
    
    def _generate_revenue_trend(self, transactions: List[Dict]) -> List[Dict]:
        """Generar datos de tendencia de ingresos"""
        # Agrupar por fecha
        daily_data = {}
        
        for t in transactions:
            if t['type'] == 'sale' and t['status'] == 'validated':
                date = t['date'][:10]  # YYYY-MM-DD
                if date not in daily_data:
                    daily_data[date] = {'date': date, 'revenue': 0, 'expenses': 0}
                daily_data[date]['revenue'] += t['amount']
        
        for t in transactions:
            if t['type'] in ['purchase', 'expense'] and t['status'] == 'validated':
                date = t['date'][:10]
                if date not in daily_data:
                    daily_data[date] = {'date': date, 'revenue': 0, 'expenses': 0}
                daily_data[date]['expenses'] += t['amount']
        
        # Ordenar por fecha
        sorted_data = sorted(daily_data.values(), key=lambda x: x['date'])
        
        return sorted_data
    
    def _generate_expense_distribution(self, transactions: List[Dict]) -> List[Dict]:
        """Generar distribución de gastos por categoría"""
        category_data = {}
        
        for t in transactions:
            if t['type'] in ['purchase', 'expense'] and t['status'] == 'validated':
                category = t.get('category', 'Otros')
                if category not in category_data:
                    category_data[category] = {'category': category, 'amount': 0, 'count': 0}
                category_data[category]['amount'] += t['amount']
                category_data[category]['count'] += 1
        
        # Ordenar por monto
        sorted_data = sorted(category_data.values(), key=lambda x: x['amount'], reverse=True)
        
        return sorted_data
    
    def _generate_revenue_by_category(self, transactions: List[Dict]) -> List[Dict]:
        """Generar ingresos por categoría"""
        category_data = {}
        
        for t in transactions:
            if t['type'] == 'sale' and t['status'] == 'validated':
                category = t.get('category', 'Otros')
                if category not in category_data:
                    category_data[category] = {'category': category, 'amount': 0, 'count': 0}
                category_data[category]['amount'] += t['amount']
                category_data[category]['count'] += 1
        
        # Ordenar por monto
        sorted_data = sorted(category_data.values(), key=lambda x: x['amount'], reverse=True)
        
        return sorted_data
    
    def _calculate_category_distribution(self, transactions: List[Dict]) -> Dict:
        """Calcular distribución por categoría"""
        total_revenue = sum(
            t['amount'] for t in transactions 
            if t['type'] == 'sale' and t['status'] == 'validated'
        )
        
        total_expenses = sum(
            t['amount'] for t in transactions 
            if t['type'] in ['purchase', 'expense'] and t['status'] == 'validated'
        )
        
        revenue_categories = self._generate_revenue_by_category(transactions)
        expense_categories = self._generate_expense_distribution(transactions)
        
        # Calcular porcentajes
        for cat in revenue_categories:
            cat['percentage'] = (cat['amount'] / total_revenue * 100) if total_revenue > 0 else 0
        
        for cat in expense_categories:
            cat['percentage'] = (cat['amount'] / total_expenses * 100) if total_expenses > 0 else 0
        
        return {
            'revenue': {
                'total': total_revenue,
                'categories': revenue_categories
            },
            'expenses': {
                'total': total_expenses,
                'categories': expense_categories
            }
        }
    
    def _compare_with_previous(self, transactions: List[Dict], period: str) -> Dict:
        """Comparar con período anterior"""
        current_transactions = self._filter_by_period(transactions, period)
        
        # Determinar período anterior
        if period == 'current_month':
            previous_period = 'last_month'
        else:
            previous_period = 'current_month'
        
        previous_transactions = self._filter_by_period(transactions, previous_period)
        
        # Calcular métricas actuales
        current_summary = self._calculate_summary(current_transactions)
        
        # Calcular métricas anteriores
        previous_summary = self._calculate_summary(previous_transactions)
        
        # Calcular variaciones
        revenue_variation = self._calculate_variation(
            current_summary['revenue']['total'],
            previous_summary['revenue']['total']
        )
        
        expenses_variation = self._calculate_variation(
            current_summary['expenses']['total'],
            previous_summary['expenses']['total']
        )
        
        net_income_variation = self._calculate_variation(
            current_summary['net_income']['total'],
            previous_summary['net_income']['total']
        )
        
        return {
            'current_period': period,
            'previous_period': previous_period,
            'revenue': revenue_variation,
            'expenses': expenses_variation,
            'net_income': net_income_variation
        }
    
    def _calculate_variation(self, current: float, previous: float) -> Dict:
        """Calcular variación entre dos valores"""
        if previous == 0:
            variation = 0.0
            variation_type = 'neutral'
        else:
            variation = ((current - previous) / previous) * 100
            variation_type = 'positive' if variation > 0 else 'negative' if variation < 0 else 'neutral'
        
        return {
            'current': current,
            'previous': previous,
            'variation': variation,
            'variation_type': variation_type
        }
    
    def get_client_dashboard(self, client_id: str) -> Optional[Dict]:
        """
        Obtener dashboard de cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Datos del dashboard o None si no existe
        """
        return self.client_data.get(client_id)
    
    def export_dashboard(self, client_id: str, format: str = 'json') -> Optional[str]:
        """
        Exportar dashboard
        
        Args:
            client_id: ID del cliente
            format: Formato de exportación (json, csv)
            
        Returns:
            Datos exportados o None
        """
        dashboard = self.get_client_dashboard(client_id)
        if not dashboard:
            return None
        
        if format == 'json':
            return json.dumps(dashboard, indent=2, default=str)
        elif format == 'csv':
            # Implementar exportación CSV
            return self._export_to_csv(dashboard)
        else:
            return None
    
    def _export_to_csv(self, dashboard: Dict) -> str:
        """Exportar dashboard a CSV"""
        # Implementación básica de exportación CSV
        lines = []
        
        # Resumen
        lines.append('Summary')
        lines.append('Metric,Value')
        lines.append(f"Total Revenue,{dashboard['summary']['revenue']['total']}")
        lines.append(f"Total Expenses,{dashboard['summary']['expenses']['total']}")
        lines.append(f"Net Income,{dashboard['summary']['net_income']['total']}")
        lines.append(f"Margin,{dashboard['summary']['net_income']['margin']}")
        lines.append('')
        
        # Transacciones
        lines.append('Transactions')
        lines.append('Date,Type,Amount,Category,Status')
        for t in dashboard['transactions']:
            lines.append(f"{t['date']},{t['type']},{t['amount']},{t.get('category', '')},{t['status']}")
        
        return '\n'.join(lines)


class DashboardExporter:
    """Exportador de dashboard para Looker Studio"""
    
    def __init__(self):
        """Inicializar exportador"""
        self.export_formats = ['json', 'csv', 'looker_studio']
    
    def prepare_for_looker_studio(self, dashboard_data: Dict) -> Dict:
        """
        Preparar datos para Looker Studio
        
        Args:
            dashboard_data: Datos del dashboard
            
        Returns:
            Diccionario con datos preparados para Looker Studio
        """
        # Transformar datos al formato esperado por Looker Studio
        looker_data = {
            'summary': dashboard_data['summary'],
            'revenue_trend': self._format_for_looker(dashboard_data['charts']['revenue_trend']),
            'expense_distribution': self._format_for_looker(dashboard_data['charts']['expense_distribution']),
            'revenue_by_category': self._format_for_looker(dashboard_data['charts']['revenue_by_category']),
            'comparison': dashboard_data['comparison']
        }
        
        return looker_data
    
    def _format_for_looker(self, data: List[Dict]) -> List[Dict]:
        """Formatear datos para Looker Studio"""
        # Looker Studio espera datos en formato específico
        return data
    
    def generate_looker_studio_config(self) -> Dict:
        """
        Generar configuración para Looker Studio
        
        Returns:
            Diccionario con configuración
        """
        config = {
            'data_source': 'google_sheets',
            'refresh_interval': '15_minutes',
            'charts': [
                {
                    'type': 'scorecard',
                    'title': 'Ingresos Totales',
                    'metric': 'revenue.total'
                },
                {
                    'type': 'scorecard',
                    'title': 'Egresos Totales',
                    'metric': 'expenses.total'
                },
                {
                    'type': 'scorecard',
                    'title': 'Ingreso Neto',
                    'metric': 'net_income.total'
                },
                {
                    'type': 'line_chart',
                    'title': 'Evolución de Ingresos',
                    'dimension': 'date',
                    'metric': 'revenue'
                },
                {
                    'type': 'pie_chart',
                    'title': 'Distribución de Gastos',
                    'dimension': 'category',
                    'metric': 'amount'
                }
            ]
        }
        
        return config
