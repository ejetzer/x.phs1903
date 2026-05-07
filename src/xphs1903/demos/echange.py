def main():
    from xphs1903.outils.echange import Échange
    from xphs1903.outils.serial import sélection_appareil
    with Échange(sélection_appareil()) as ex:
        ex.loop()


if __name__ == '__main__':
    main()
