from django.core.management.base import BaseCommand
from exam.models import ExamSet, Question

class Command(BaseCommand):
    help = 'サンプルデータ（試験セットと問題）を投入します'

    def handle(self, *args, **options):
        self.stdout.write('サンプルデータの投入を開始します...')
        
        # 既存の試験セットを削除（オプション）
        # ExamSet.objects.all().delete()
        
        # 試験セット1: 基本情報技術者試験
        exam_set1, created = ExamSet.objects.get_or_create(
            name='基本情報技術者試験（サンプル）',
            defaults={
                'description': 'IT業界の基本的な知識を問う国家資格試験のサンプル問題です。',
                'total_questions': 40
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 試験セット作成: {exam_set1.name}'))
            
            # サンプル問題を40問作成
            questions_data = [
                {
                    'question_text': '2進数の1010と1100を加算した結果を10進数で表すといくつか。',
                    'choice_1': '20',
                    'choice_2': '22',
                    'choice_3': '24',
                    'choice_4': '26',
                    'correct_answer': 2,
                    'explanation': '2進数の1010は10進数で10、1100は12です。10 + 12 = 22となります。',
                    'explanation_1': '20は2進数の10100です。',
                    'explanation_2': '正解です。1010(10) + 1100(12) = 22です。',
                    'explanation_3': '24は2進数の11000です。',
                    'explanation_4': '26は2進数の11010です。',
                },
                {
                    'question_text': 'OSI参照モデルにおいて、データリンク層に該当するものはどれか。',
                    'choice_1': 'TCP',
                    'choice_2': 'IP',
                    'choice_3': 'Ethernet',
                    'choice_4': 'HTTP',
                    'correct_answer': 3,
                    'explanation': 'Ethernetはデータリンク層（第2層）のプロトコルです。',
                    'explanation_1': 'TCPはトランスポート層（第4層）のプロトコルです。',
                    'explanation_2': 'IPはネットワーク層（第3層）のプロトコルです。',
                    'explanation_3': '正解です。Ethernetはデータリンク層のプロトコルです。',
                    'explanation_4': 'HTTPはアプリケーション層（第7層）のプロトコルです。',
                },
                {
                    'question_text': 'データベースの正規化において、第1正規形を満たす条件はどれか。',
                    'choice_1': '主キーが存在する',
                    'choice_2': '繰り返し項目が存在しない',
                    'choice_3': '部分関数従属が存在しない',
                    'choice_4': '推移的関数従属が存在しない',
                    'correct_answer': 2,
                    'explanation': '第1正規形は、繰り返し項目（配列など）が存在せず、すべての属性が単一値であることが条件です。',
                    'explanation_1': '主キーの存在は正規形の前提条件ですが、第1正規形の特徴ではありません。',
                    'explanation_2': '正解です。第1正規形では繰り返し項目を排除します。',
                    'explanation_3': '部分関数従属の排除は第2正規形の条件です。',
                    'explanation_4': '推移的関数従属の排除は第3正規形の条件です。',
                },
            ]
            
            # 最初の3問は詳細なデータ、残りはテンプレート
            for i, q_data in enumerate(questions_data, 1):
                Question.objects.create(exam_set=exam_set1, **q_data)
            
            # 残りの問題を生成（4〜40問目）
            for i in range(4, 41):
                Question.objects.create(
                    exam_set=exam_set1,
                    question_text=f'問題{i}: これはサンプル問題{i}です。実際の問題に置き換えてください。\n選択肢を確認し、正しいものを選んでください。',
                    choice_1=f'選択肢1: サンプル回答A（問題{i}）',
                    choice_2=f'選択肢2: サンプル回答B（問題{i}）',
                    choice_3=f'選択肢3: サンプル回答C（問題{i}）',
                    choice_4=f'選択肢4: サンプル回答D（問題{i}）',
                    correct_answer=(i % 4) + 1,  # 1〜4をローテーション
                    explanation=f'問題{i}の解説です。正解は選択肢{(i % 4) + 1}です。実際の問題では詳細な解説を記載してください。',
                    explanation_1=f'選択肢1の説明: この選択肢は{"正解" if (i % 4) + 1 == 1 else "不正解"}です。',
                    explanation_2=f'選択肢2の説明: この選択肢は{"正解" if (i % 4) + 1 == 2 else "不正解"}です。',
                    explanation_3=f'選択肢3の説明: この選択肢は{"正解" if (i % 4) + 1 == 3 else "不正解"}です。',
                    explanation_4=f'選択肢4の説明: この選択肢は{"正解" if (i % 4) + 1 == 4 else "不正解"}です。',
                )
            
            self.stdout.write(self.style.SUCCESS(f'✓ 問題40問を作成しました'))
        else:
            self.stdout.write(self.style.WARNING(f'! 試験セット "{exam_set1.name}" は既に存在します'))
        
        # 試験セット2: 応用情報技術者試験
        exam_set2, created = ExamSet.objects.get_or_create(
            name='応用情報技術者試験（サンプル）',
            defaults={
                'description': 'より高度なIT知識を問う国家資格試験のサンプル問題です。',
                'total_questions': 40
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 試験セット作成: {exam_set2.name}'))
            
            # 簡易的なサンプル問題を40問作成
            for i in range(1, 41):
                Question.objects.create(
                    exam_set=exam_set2,
                    question_text=f'応用問題{i}: これはサンプル問題{i}です。実際の問題に置き換えてください。\nより高度な内容について問う問題です。',
                    choice_1=f'選択肢1: 応用レベルの回答A（問題{i}）',
                    choice_2=f'選択肢2: 応用レベルの回答B（問題{i}）',
                    choice_3=f'選択肢3: 応用レベルの回答C（問題{i}）',
                    choice_4=f'選択肢4: 応用レベルの回答D（問題{i}）',
                    correct_answer=((i + 1) % 4) + 1,
                    explanation=f'応用問題{i}の解説です。正解は選択肢{((i + 1) % 4) + 1}です。より詳細な解説を記載してください。',
                    explanation_1=f'選択肢1の詳細説明（応用レベル）',
                    explanation_2=f'選択肢2の詳細説明（応用レベル）',
                    explanation_3=f'選択肢3の詳細説明（応用レベル）',
                    explanation_4=f'選択肢4の詳細説明（応用レベル）',
                )
            
            self.stdout.write(self.style.SUCCESS(f'✓ 問題40問を作成しました'))
        else:
            self.stdout.write(self.style.WARNING(f'! 試験セット "{exam_set2.name}" は既に存在します'))
        
        self.stdout.write(self.style.SUCCESS('\n=== サンプルデータの投入が完了しました ==='))
        self.stdout.write(f'試験セット数: {ExamSet.objects.count()}')
        self.stdout.write(f'問題数: {Question.objects.count()}')
        self.stdout.write('\n管理画面から問題内容を編集できます: http://127.0.0.1:8000/admin/')