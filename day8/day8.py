def digits_to_layers(digits, width, height):
    pointer = 0
    layers = []
    while pointer < len(digits):
        layer_size = width*height
        layers.append(digits[pointer : pointer + layer_size])
        pointer += layer_size

    return layers

def puzzle1(input):
    layers = digits_to_layers(input, 25, 6)
    zeroes = [layer.count('0') for layer in layers]
    layer_with_min_zeroes = zeroes.index(min(zeroes))
    result = layers[layer_with_min_zeroes].count('1') * layers[layer_with_min_zeroes].count('2')
    return result

def get_pixel_value(pixel, layers):
    for layer in layers:
        if layer[pixel] == '0':
            return "█"
        elif layer[pixel] == '1':
            return '░'

    assert False, "We should not get here. That means that none of the layers have a pixel here.."



def stack_layers(input, width, height):
    image = ['x']*width*height
    layers = digits_to_layers(input, width, height)
    for pixel in range(width * height):
        image[pixel] = get_pixel_value(pixel, layers)
    #print(image)
    return image

def puzzle2(input):
    image = stack_layers(input, 25, 6)
    image = ''.join(image)
    rows = [image[r*25:(r+1)*25] for r in range(6)]
    return '\n'.join(rows)



with open('input.txt') as f:
    i = f.read()
    print(F"The result of puzzle 1 is {puzzle1(i)}")
    print(F"The result of puzzle 1 is \n{puzzle2(i)}")