    for col in range(cell_num):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * cell_size, 0, cell_size, cell_size)  
                        pygame.draw.rect(screen, grass_colour, grass_rect)