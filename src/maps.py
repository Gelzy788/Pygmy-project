from PIL import Image
import numpy as np


def create_collision_map(image_path):
    """
    Создает матрицу коллизий из изображения, где:
    0 - белый цвет (проходимая область)
    1 - черный цвет (непроходимая область)
    """
    # Открываем изображение
    img = Image.open(image_path)

    # Преобразуем в черно-белый формат
    img = img.convert('L')

    # Преобразуем в numpy массив
    img_array = np.array(img)

    # Создаем бинарную матрицу
    # Если пиксель ближе к черному (< 128), то ставим 1, иначе 0
    binary_matrix = (img_array < 128).astype(int)

    return binary_matrix


def print_collision_map(matrix):
    """
    Выводит матрицу в консоль в читаемом виде
    """
    for row in matrix:
        print(' '.join(['#' if cell == 1 else '.' for cell in row]))


def save_collision_map(matrix, output_path):
    """
    Сохраняет матрицу в текстовый файл
    """
    with open(output_path, 'w') as f:
        for row in matrix:
            f.write(','.join(map(str, row)) + '\n')


# Пример использования
if __name__ == "__main__":
    # Путь к изображению
    file_name = input()
    image_path = f"data/{file_name}.png"

    try:
        # Создаем матрицу коллизий
        collision_matrix = create_collision_map(image_path)

        # Выводим матрицу в консоль
        print("Матрица коллизий (# - препятствие, . - проходимая область):")
        print_collision_map(collision_matrix)

        # Сохраняем матрицу в файл
        save_collision_map(collision_matrix, f"{file_name}.txt")
        print(f"\nМатрица сохранена в файл {file_name}.txt")

        # Выводим размеры матрицы
        print(f"Размеры матрицы: {collision_matrix.shape}")

    except FileNotFoundError:
        print(f"Ошибка: Файл {image_path} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
