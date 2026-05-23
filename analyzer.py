import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from io import BytesIO


class Analyzer:

    @staticmethod
    def create_chart(df):
        if df.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(
            df['entry_date'],
            df['mood_score'],
            marker='o'
        )

        ax.set_title('Динамика настроения')
        ax.set_ylabel('Настроение')

        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = BytesIO()

        plt.savefig(buffer, format='png')

        buffer.seek(0)

        plt.close()

        return buffer