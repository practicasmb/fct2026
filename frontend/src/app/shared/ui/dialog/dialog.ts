import {
  ChangeDetectionStrategy, Component, input, output, computed,
} from '@angular/core';

@Component({
  selector: 'ui-dialog',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (open()) {
      <div class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="fixed inset-0 bg-black/80" (click)="openChange.emit(false)"></div>
        <div class="relative z-50">
          <ng-content />
        </div>
      </div>
    }
  `,
})
export class DialogComponent {
  open = input<boolean>(false);
  openChange = output<boolean>();
}

@Component({
  selector: 'ui-dialog-content',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class]="classes()">
      <ng-content />
      <button
        class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        (click)="closed.emit()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        <span class="sr-only">Close</span>
      </button>
    </div>
  `,
})
export class DialogContentComponent {
  class = input<string>('');
  closed = output<void>();
  classes = computed(() => ['grid w-full max-w-lg gap-4 border bg-background p-6 shadow-lg sm:rounded-lg', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-dialog-header',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="flex flex-col space-y-1.5 text-center sm:text-left"><ng-content /></div>`,
})
export class DialogHeaderComponent {}

@Component({
  selector: 'ui-dialog-footer',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2"><ng-content /></div>`,
})
export class DialogFooterComponent {}

@Component({
  selector: 'ui-dialog-title',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<h2 class="text-lg font-semibold leading-none tracking-tight"><ng-content /></h2>`,
})
export class DialogTitleComponent {}

@Component({
  selector: 'ui-dialog-description',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p class="text-sm text-muted-foreground"><ng-content /></p>`,
})
export class DialogDescriptionComponent {}
