import {
  ChangeDetectionStrategy,
  Component,
  input,
  computed,
} from '@angular/core';
import { TagModule } from 'primeng/tag';

export type BadgeVariant = 'default' | 'info' | 'success' | 'warning' | 'danger';
export type BadgeSize    = 'default' | 'sm' | 'lg';

// p-tag acepta estos valores en [severity]
const VARIANT_MAP: Record<BadgeVariant, {
  severity?: 'info' | 'success' | 'warn' | 'danger' | 'secondary' | 'contrast';
}> = {
  default:  { severity: 'secondary' },
  info:     { severity: 'info' },
  success:  { severity: 'success' },
  warning:  { severity: 'warn' },
  danger:   { severity: 'danger' },
};

// Solo tamaño de fuente y padding — el ancho lo dicta el texto
const SIZE_MAP: Record<BadgeSize, string> = {
  default: 'text-xs',
  sm:      'text-[10px]',
  lg:      'text-sm',
};

@Component({
  selector: 'ui-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [TagModule],
  templateUrl: './badge.component.html',
})
export class BadgeComponent {
  value      = input<string>('');
  variant    = input<BadgeVariant>('default');
  size       = input<BadgeSize>('default');
  styleClass = input<string>('');

  options   = computed(() => VARIANT_MAP[this.variant()]);
  sizeClass = computed(() => SIZE_MAP[this.size()]);
}