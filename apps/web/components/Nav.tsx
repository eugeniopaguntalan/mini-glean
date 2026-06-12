'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { typography } from '@/lib/theme'

interface NavLink {
  href: string
  label: string
}

const LINKS: NavLink[] = [
  { href: '/', label: 'Documents' },
  { href: '/chat', label: 'Chat' },
]

/**
 * Top app bar (MD3) with the MiniGlean wordmark and primary navigation.
 * The active route is highlighted with the primary color and `aria-current`.
 */
export function Nav() {
  const pathname = usePathname()

  return (
    <header className="bg-surface border-b border-outline-variant">
      <nav
        aria-label="Primary"
        className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6"
      >
        <Link
          href="/"
          className={`${typography.title.large} text-primary font-semibold`}
        >
          MiniGlean
        </Link>

        <ul className="flex items-center gap-1">
          {LINKS.map((link) => {
            const isActive =
              link.href === '/'
                ? pathname === '/'
                : pathname.startsWith(link.href)

            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={isActive ? 'page' : undefined}
                  className={[
                    typography.label.large,
                    'rounded-full px-4 py-2 transition-colors',
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container'
                      : 'text-on-surface-variant hover:bg-surface-variant',
                  ].join(' ')}
                >
                  {link.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </header>
  )
}
