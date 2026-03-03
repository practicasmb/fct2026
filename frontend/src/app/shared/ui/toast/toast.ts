import {
  ChangeDetectionStrategy, Component, input, output, computed, Injectable, signal,
} from '@angular/core';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
  duration?: number;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts = signal<Toast[]>([]);

  add(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).slice(2);
    this.toasts.update(t => [...t, { ...toast, id }]);
    setTimeout(() => this.dismiss(id), toast.duration ?? 4000);
  }

  dismiss(id: string) {
    this.toasts.update(t => t.filter(x => x.id !== id));
  }

  toast(opts: Omit<Toast, 'id'>) { this.add(opts); }
}

@Component({
  selector: 'ui-toast',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class]="classes()">
      <div class="grid gap-1">
        @if (title()) { <div class="text-sm font-semibold">{{ title() }}</div> }
        @if (description()) { <div class="text-sm opacity-90">{{ description() }}</div> }
      </div>
      <button class="absolute right-2 top-2 rounded-md p-1 opacity-70 hover:opacity-100" (click)="dismissed.emit()">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
  `,
})
export class ToastComponent {
  title = input<string>('');
  description = input<string>('');
  variant = input<'default' | 'destructive'>('default');
  dismissed = output<void>();

  classes = computed(() => {
    const base = 'pointer-events-auto relative flex w-full items-start justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all';
    const variants: Record<string, string> = {
      default: 'border bg-background text-foreground',
      destructive: 'destructive group border-destructive bg-destructive text-destructive-foreground',
    };
    return [base, variants[this.variant()]].join(' ');
  });
}
